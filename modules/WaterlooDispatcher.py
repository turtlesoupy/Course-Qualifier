import os
import re
import sys
import time
import urllib
import logging
import threading
import itertools
import simplejson
import WaterlooCatalog
import WaterlooCourseSection
import QualifierExceptions
from operator import attrgetter
from WaterlooCourse import WaterlooCourse

TOO_MANY_COMBINATIONS = 5000
TOO_MANY_SEARCH_COMBINATIONS = 10000

try:
    import Databases
    from pysqlite2 import dbapi2 as sqlite
    enableStatistics = True
    statisticsCon = sqlite.connect( Databases.waterlooStatistics)
except ImportError:
    enableStatistics = False

def cross(*args):
    ans = [[]]
    for arg in args:
        ans = [x+[y] for x in ans for y in arg]
    return ans

class WaterlooDesiredCourse:
    directRE = re.compile(r"\s*([A-Za-z]+)\s*(\d\d\d\w*)")
    def __init__(self, courseQuery, options):
        self.query = courseQuery.strip()
        m = self.directRE.match(courseQuery)
        if m:
            self.subject = m.group(1).upper()
            self.code    = m.group(2).upper()
            self.doSearch = False
        else:
            self.doSearch = True

        self.options = options

    def __cmp__( self, other ):
        return cmp(str(self), str( other ) )

    def __hash__( self ):
        return hash(str( self ))

    def __str__(self):
        return self.query
    
class WaterlooDispatcher(object):
    def __init__( self, requestDict):
        self.session = 0
        self.desiredCourses = []
        self.qualifiedSectionList = []
        self.validCatalogList = []
        self.conflictingSections = set()
        self.conflictingMessages = []
        self.options = {}

        self.initializeFromRequestDict( requestDict )

    def initializeFromRequestDict(self, requestDict ):
        self.options = requestDict["options"]
        seenCourses = set()

        if len( requestDict["courses"] ) > 15:
            raise QualifierExceptions.QualifierException("Too many courses - must be under 15")

        for course in requestDict["courses"]:
            if len(course["course_query"].strip()) == 0:
                continue
            try:
                realCourse = WaterlooDesiredCourse(course["course_query"], course["options"])
            except QualifierExceptions.InvalidInput:
                logging.warning( "Course not valid: %s %s (too short)" % ( course["course_subject"], course["course_code"] ) )
                continue

            if realCourse in seenCourses:
                logging.info( "Skipping duplicate course %s", realCourse )
                continue

            seenCourses.add(realCourse)
            self.desiredCourses.append(realCourse)

        self.session = requestDict["term"]

    def filterGroupOptions(self, courseGroup, courseOptions):
        hasTutorials = courseOptions['tutorials']
        hasTests     = courseOptions['tests']
        hasOther     = courseOptions['other']

        def courseWorks(c):
            if c.type == "TUT" and not hasTutorials:
                return False

            if c.type == "TST" and not hasTests:
                return False

            if c.type not in ("TST", "TUT", "LEC") and not hasOther:
                return False

            return True

        return [e for e in courseGroup if courseWorks(e)]

    def groupHasRequiredSections(self, courseGroup, courseOptions):
        requiredSections = set(e for e in courseOptions["sections"] if e)
        for course in courseGroup:
            goodSection = None
            for section in course.sections:
                if section.sectionNum in requiredSections:
                    goodSection = section
            if goodSection:
                course.sections = [e for e in course.sections if e.sectionNum in requiredSections]

            requiredSections -= set(e.sectionNum for e in course.sections )

        return len(requiredSections) <= 0

    def filterSections(self, sections):
        ret = sections
        if "show_full_courses" in self.options and self.options["show_full_courses"] == False:
            ret = [e for e in ret if not e.full()]

        if self.options["start_later_than_hour"] != "" and self.options["start_later_than_minute"] != "":
            minTime = 60*60*int(self.options["start_later_than_hour"]) + 60*int(self.options["start_later_than_minute"] )
            if self.options[ "start_later_than_hour" ] == "12":
                minTime -= 12*60*60
            if self.options['start_later_than_ampm'] == "PM":
                minTime += 60*60*12 
            ret = [e for e in ret if e.startsAfter(minTime)]
        

        if self.options["ends_earlier_than_hour"] != "" and self.options["ends_earlier_than_minute"] != "":
            maxTime = 60*60*int(self.options["ends_earlier_than_hour"]) + 60*int(self.options["ends_earlier_than_minute"] )
            if self.options[ "ends_earlier_than_hour" ] == "12":
                maxTime -= 12*60*60
            if self.options['ends_earlier_than_ampm'] == "PM":
                maxTime += 60*60*12
            ret = [e for e in ret if e.endsEarlier(maxTime)]

        return ret

    def dispatch(self):
        toQualify  = [] 
        toSearch   = []
        allCourses = []

        for desiredCourse in self.desiredCourses:
            if desiredCourse.doSearch:
                searchObjects = [self.filterGroupOptions(e, desiredCourse.options) \
                        for e in WaterlooCourse.coursesFromSearch(desiredCourse.query, self.session)]

                for group in searchObjects:
                    for course in group:
                        course.sections = self.filterSections(course.sections)

                filteredObjects = [g for g in searchObjects if all(len(c.sections) > 0 for c in g)]
                if len(filteredObjects) == 0:
                    raise QualifierExceptions.QualifierException("No courses found for query '%s' with given options" % desiredCourse.query)

                #We get back something of the form[[AMATH 250 TUT, AMATH 250 LEC], [CS 245 LEC]]
                toSearch.append(filteredObjects)
                for courseGroup in filteredObjects:
                    allCourses.extend(courseGroup)
            else:
                codeCourses  = WaterlooCourse.coursesFromCode(desiredCourse.subject, \
                        desiredCourse.code, self.session)

                filteredCourses = self.filterGroupOptions(codeCourses, desiredCourse.options)
                if len(filteredCourses) == 0:
                    raise QualifierExceptions.QualifierException("No course matches filters for '%s'" % desiredCourse.query)

                for course in filteredCourses:
                    course.sections = self.filterSections(course.sections)
                    if len(course.sections) == 0:
                        raise QualifierExceptions.QualifierException("No sections found matching filters for '%s %s'" % (course.courseName, course.type))

                if not self.groupHasRequiredSections(filteredCourses, desiredCourse.options):
                    raise QualifierExceptions.MissingRequiredSectionsException()

                toQualify.extend(filteredCourses)
                allCourses.extend(filteredCourses)

        self.checkBlowup(toQualify, toSearch)

        #Combinatorial combinations of all sections for _direct_ courses
        self.qualifyCourses(toQualify[:])

        #Special behaviour: add in search courses
        if len(toSearch) > 0:
            validCatalogs = self.qualifiedSectionList[:]
            self.qualifiedSectionList = []
            self.addSearchCourses(validCatalogs, toSearch)

        self.validCatalogList = [WaterlooCatalog.WaterlooCatalog(x) for x in self.qualifiedSectionList]
        self.writeStatistics()

        return self.makeJson(allCourses)

    # Core algorithm for computing conflicts
    def qualifyCourses(self, remainingCourses, sectionAcc=[]):
        if len( remainingCourses ) == 0:
            if len( sectionAcc ) > 0 and self.checkCatalog( sectionAcc):
                self.qualifiedSectionList.append(sectionAcc)
        else:
            currentCourse = remainingCourses.pop()
            for currSection in currentCourse.sections:
                for otherSection in sectionAcc:
                    if currSection.conflictsWith(otherSection):
                        self.conflictingSections.add((currSection, otherSection))
                        break
                else:
                    self.qualifyCourses(remainingCourses[:], sectionAcc[:] + [currSection]) 
                    #Side effect! (beats constructing the object via return values in the recursion tree)

     
    def checkBlowup(self, courses, searchList):
        #Abort if we will never finish qualifying (blow-up)
        numClasses = 1
        if len( courses ) > 1:
            numClasses = reduce( lambda x,y : x * y, (max(len(e.sections),1) for e in courses ) ) 
            if numClasses > TOO_MANY_COMBINATIONS:
                raise QualifierExceptions.TooManySchedulesException(numClasses)

        for courseOption in searchList:
            numClasses *= sum(sum(len(x.sections) for x in courseGroup) for courseGroup in courseOption)

        if numClasses > TOO_MANY_SEARCH_COMBINATIONS:
            raise QualifierExceptions.TooManySchedulesException( numClasses )

    def checkCatalog(self, catalog):
        if "obey_related" in self.options and self.options["obey_related"]:
            requiredSections  = set("%s %s" % (e.parent.courseName, e.related1) for e in catalog if e.related1 and e.related1 != '99')
            requiredSections |= set("%s %s" % (e.parent.courseName, e.related2) for e in catalog if e.related2 and e.related2 != '99')
            hasSections = set("%s %s" % ( e.parent.courseName, e.sectionNum) for e in catalog)
            
            if len(requiredSections - hasSections) > 0:
                for section in requiredSections - hasSections:
                    self.conflictingMessages.append( "Catalog lacks required section %s" % section )
                return False

        return True

    # Add back in search courses after we have figured out 
    # non-conflicting catalogs (without search courses)
    def addSearchCourses(self, validCatalogs, searchCourses):
        #Cartesian product if we have multiple search courses (e.g. "CS 2*" and "CS 4*" were entered)
        searchList = cross(*searchCourses)
        for searchables in searchList:
            possibleCourses = []
            for classGroup in searchables:
                possibleCourses.extend(classGroup)
            if len(validCatalogs) == 0:
                self.qualifyCourses(possibleCourses, []) #Side effect!
            else:
                for catalog in validCatalogs:
                    self.qualifyCourses(possibleCourses[:], catalog[:]) #Side effect!

    def writeStatistics( self ):
        if not enableStatistics:
            return

        cursor = statisticsCon.cursor()
        cursor.execute( "INSERT INTO qualify_requests (id, time,ip,term) VALUES\
        (NULL, datetime('now'), ?,?)", (os.environ["REMOTE_ADDR"],self.session) )
  
        request_id = cursor.lastrowid
        #TODO: use executemany
        for course in self.desiredCourses:
            cursor.execute( "INSERT INTO qualify_request_courses (id, request_id, subject, code ) VALUES \
            (NULL, %d, ?, ?)" % request_id, (course.subject, course.code ) )

        for sections in self.conflictingSections:
            namesToInsert = sorted( e.courseName for e in sections )
            cursor.execute( "INSERT INTO qualify_request_conflicts (id, request_id, course1, course2 ) VALUES \
            (NULL, ?, ?, ?)", ( request_id, namesToInsert[0], namesToInsert[1] ) )
             
        
        statisticsCon.commit()
        cursor.close()


    def makeErrorJson( self, errorString ):
        return {"error": errorString}

    def makeJson( self, startCourses ):
        return { "courses": dict( (e.uniqueName, e.getJson()) for e in startCourses),
                 "catalogs": [e.getJson() for e in self.validCatalogList],
                 "conflicts": {
                                "courses":  [ (o.getReferenceJson(), t.getReferenceJson() ) for o,t in self.conflictingSections ],
                                "messages": self.conflictingMessages 
                                },
                 "valid_metrics" : WaterlooCatalog.WaterlooCatalog.validMetrics,
                 "section_information": WaterlooCourseSection.WaterlooCourseSection.sectionInformation
                }
