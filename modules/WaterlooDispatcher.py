import os
import re
import sys
import urllib
import logging
import simplejson
import Dispatcher
import WaterlooCourse
import WaterlooCourseSection
import WaterlooCatalog
import QualifierExceptions
import threading
import itertools
import time
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import NavigableString

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
    def __init__( self, courseSubject, courseCode, options ):
        self.subject = courseSubject.upper()
        self.code = courseCode.upper()
        self.options = options
	if (len(self.code) > 0 and self.code[-1] == "*"):
		self.doSearch = True
		self.code = self.code[:-1]
	else:
		self.doSearch = False
		if len( self.code ) < 3:
		    raise QualifierExceptions.InvalidInput()


    def __cmp__( self, other ):
        return cmp(str(self), str( other ) )

    def __hash__( self ):
        return hash(str( self ))

    def __str__( self ):
        return "%s %s" % ( self.subject, self.code )

class WaterlooDispatcher( Dispatcher.Dispatcher ):
    postURL = "http://www.adm.uwaterloo.ca/cgi-bin/cgiwrap/infocour/salook.pl"
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
            raise QualifierExceptions.QualifierException( "Too many courses - must be under 15 " )

        for course in requestDict["courses"]:
            if len( course["course_subject"].strip() ) == 0 or len(course["course_code"].strip()) == 0:
                continue

            try:
                realCourse = WaterlooDesiredCourse( course["course_subject"], course["course_code"], course["options"])
            except QualifierExceptions.InvalidInput:
                logging.warning( "Course not valid: %s %s (too short)" % ( course["course_subject"], course["course_code"] ) )
                continue

            if realCourse in seenCourses:
                logging.info( "Skipping duplicate course %s", realCourse )
                continue

            seenCourses.add( realCourse )
            self.desiredCourses.append( realCourse )

        self.session = requestDict["term"]

    def getHTML( self, course, graduate=False ):
        params = urllib.urlencode({
                    "level": graduate and "grad" or "under",
                    "sess": self.session,
                    "subject": course.subject,
                    "cournum": course.code
                    })
        f = urllib.urlopen( self.postURL, params )
        try:
            html = f.read()
        finally:
            f.close()

        return html


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
     
    class HTMLFetchThread( threading.Thread ):
        def __init__( self, postURL, session, course, graduate=False):
            self.postURL = postURL
            self.session = session
            self.course = course
            self.graduate = graduate
            self.html = ""
            threading.Thread.__init__( self )

        def run( self ):
            params = urllib.urlencode({
                        "level": self.graduate and "grad" or "under",
                        "sess": self.session,
                        "subject": self.course.subject,
                        "cournum": self.course.code
                        })
            f = urllib.urlopen( self.postURL, params )
            try:
                html = f.read()
            finally:
                f.close()
            
            self.html = html



    def dispatch( self ):
        totalTimeout = 20.0

        toQualify = [] 
        toSearch = []
        allCourses = []

        htmlThreads = []
        htmlList = []
        #Tidy up this later
        for desiredCourse in self.desiredCourses:
            yatta = self.HTMLFetchThread( self.postURL, self.session, desiredCourse )
            yatta.start()
            htmlThreads.append( yatta )

        for thread in htmlThreads:
            startTime = time.time()
            thread.join(totalTimeout)
            totalTimeout -= (time.time() - startTime)
            if totalTimeout <= 0:
                break
            
            htmlList.append( thread.html )

        if totalTimeout < 0:
            raise QualifierExceptions.QualifierException( "Timeout when communicating to Waterloo servers \n Is the Waterloo website down?")

        for desiredCourse, realHtml in zip(self.desiredCourses, htmlList):
            #html = self.getHTML( desiredCourse )
            html = realHtml
            try:
                courseObjects = WaterlooCourse.constructCourses( html, desiredCourse.options, self.options )
            except QualifierExceptions.CourseMissingException:
                #try grad level
                html = self.getHTML( desiredCourse, True )
                try:
                    courseObjects = WaterlooCourse.constructCourses( html, desiredCourse.options, self.options )
                except QualifierExceptions.CourseMissingException:
                    logging.warning( "Unable to find any courses to match %s %s" % (desiredCourse.subject, desiredCourse.code ) )
                    continue
	    if desiredCourse.doSearch:
		    groups = []
		    for k,g in itertools.groupby(courseObjects, lambda x:x.courseName): #Pairing AMATH 250 LEC with TUT
			    groups.append(list(g))
		    toSearch.append(groups)
	    else:
		    toQualify.extend( courseObjects )
	    allCourses.extend(courseObjects)

        self.preCheck( toQualify, toSearch )
        self.qualifyCourses( toQualify[:] )

	#Add search courses if we have any -- EXPENSIVE!
	if len(toSearch) > 0:
		validCatalogs = self.qualifiedSectionList[:]
		self.qualifiedSectionList = []
		self.addSearchCourses(validCatalogs, toSearch)

	self.validCatalogList = [WaterlooCatalog.WaterlooCatalog(x) for x in self.qualifiedSectionList]
        self.writeStatistics()

        return self.makeJson(allCourses)


    def preCheck( self, catalog, searchList ):
        #Abort if we will never finish qualifying (blow-up)
	numClasses = 1
        if len( catalog ) > 1:
            numClasses = reduce( lambda x,y : x * y, (len(e.sections) for e in catalog ) ) 
            if numClasses > 5000:
                raise QualifierExceptions.TooManySchedulesException( numClasses )

	for courseOption in searchList:
		numClasses *= sum(sum(len(x.sections) for x in courseGroup) for courseGroup in courseOption)

	if numClasses > 10000:
		raise QualifierExceptions.TooManySchedulesException( numClasses )


    def checkCatalog( self, catalog ):
        if "obey_related" in self.options and self.options["obey_related"]:
            requiredSections =  set( "%s %s" % (e.parent.courseName, e.related1) for e in catalog if e.related1 and e.related1 != '99')
            requiredSections |= set( "%s %s" % (e.parent.courseName, e.related2) for e in catalog if e.related2 and e.related2 != '99')
            hasSections = set( "%s %s" % ( e.parent.courseName, e.sectionNum) for e in catalog )
            
            if len(requiredSections - hasSections ) > 0:
                for section in requiredSections - hasSections:
                    self.conflictingMessages.append( "Catalog lacks required section %s" % section )

                return False

        return True

    def addSearchCourses(self, validCatalogs, searchCourses):
	searchList = cross(*searchCourses)
	for searchables in searchList:
		possibleCourses = []
		for classGroup in searchables:
			possibleCourses.extend(classGroup)
		if len(validCatalogs) == 0:
			self.qualifyCourses(possibleCourses, [])
		else:
			for catalog in validCatalogs:
				self.qualifyCourses(possibleCourses[:], catalog[:])

    def qualifyCourses( self, remainingCourses, sectionAcc=[] ):
        if len( remainingCourses ) == 0:
            if len( sectionAcc ) > 0 and self.checkCatalog( sectionAcc):
		self.qualifiedSectionList.append(sectionAcc)
        else:
            currentCourse = remainingCourses.pop()
            for currSection in currentCourse.sections:
                for otherSection in sectionAcc:
                    if currSection.conflictsWith( otherSection ):
                        self.conflictingSections.add( (currSection, otherSection ) )
                        break
                else:
                    self.qualifyCourses( remainingCourses[:], sectionAcc[:] + [currSection] )

    def makeErrorJson( self, errorString ):
        return { "error": errorString }

    def makeJson( self, startCourses ):
        return {  "courses": dict( (e.uniqueName, e.getJson()) for e in startCourses),
                  "catalogs": [e.getJson() for e in self.validCatalogList],
                  "conflicts": {
                                "courses":  [ (o.getReferenceJson(), t.getReferenceJson() ) for o,t in self.conflictingSections ],
                                "messages": self.conflictingMessages 
                                },
                  "valid_metrics" : WaterlooCatalog.WaterlooCatalog.validMetrics,
                  "section_information": WaterlooCourseSection.WaterlooCourseSection.sectionInformation
                }


def test():
    dispatcher = WaterlooDispatcher( "1079")
#    desiredCourse = DesiredCourse( "ECON", "101" )

    

    # print dispatcher.getHTML( 1085, desiredCourse )
    f = open( "test.html", "r" )
    html = f.read()
    f.close()

    courses = WaterlooCourse.constructCourses( html  )
    f = open( "math135.htm", "r" ) 
    html = f.read()
    f.close()
    courses.extend( WaterlooCourse.constructCourses( html ) )
    

    dispatcher.qualifyCourses( courses )
    print simplejson.dumps( dispatcher.makeJson(courses) )

if __name__ == "__main__":
    test()
