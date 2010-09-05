import re
import copy
import logging
import simplejson
import QualifierExceptions
from KeyedObject import KeyedObject
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import NavigableString
from WaterlooCourse import WaterlooCourse
from WaterlooCourseSection import WaterlooCourseSection
from WaterlooCourseOffering import WaterlooCourseOffering

whiteSpaceRE = re.compile("\s{2,}")
def cleanString(theString):
    return whiteSpaceRE.sub(" ", theString).strip()

# Parses the "salook" waterloo html page
# This is hacky, but it has to be (screen scraping)
class WaterlooCourseParser(object):
    def __init__(self, courseOptions, globalOptions):
        self.courseOptions = courseOptions
        self.globalOptions = globalOptions

    def checkCourseAgainstOptions(self, waterlooCourse ):
        hasTutorials = self.courseOptions["tutorials"]
        hasTests     = self.courseOptions["tests"]
        hasOther     = self.courseOptions["other"]

        if not hasTutorials and waterlooCourse.type.startswith("TUT"):
            return False
        if not hasTests and waterlooCourse.type.startswith("TST"):
            return False

        if not hasOther:
            for good in ("TST", "TUT", "LEC"):
                if waterlooCourse.type.startswith( good ):
                    break
            else:
                return False
            
        return True

    def checkAllCoursesAgainstOptions(self, courses):
        requiredSections = set(e for e in self.courseOptions["sections"] if e)
        for course in courses:
            goodSection = None
            for section in course.sections:
                if section.sectionNum in requiredSections:
                    goodSection = section
            if goodSection:
                course.sections = [e for e in course.sections if e.sectionNum in requiredSections]

            requiredSections -= set(e.sectionNum for e in course.sections )

        if len( requiredSections ) > 0:
            raise QualifierExceptions.MissingRequiredSectionsException( "Missing section(s) %s for %s" % 
                ( ",".join( requiredSections), courses[0].courseName ) )


    def meetsTimeOptions(self, courseSection):
        #Check for minimum start and end at parsing level
        try:
            if self.globalOptions[ "start_later_than_hour" ] != "" and self.globalOptions["start_later_than_minute"] != "":
               minTime = 60*60*int(self.globalOptions["start_later_than_hour"]) + 60*int(self.globalOptions["start_later_than_minute"] )
               if self.globalOptions[ "start_later_than_hour" ] == "12":
                   minTime -= 12*60*60

               if self.globalOptions['start_later_than_ampm'] == "PM":
                   minTime += 60*60*12

               if not courseSection.startsAfter( minTime ):
                   return False
        except (KeyError, ValueError ), e:
            pass

        try:
            if self.globalOptions[ "ends_earlier_than_hour" ] != "" and self.globalOptions["ends_earlier_than_minute"] != "":
               minTime = 60*60*int(self.globalOptions["ends_earlier_than_hour"]) + 60*int(self.globalOptions["ends_earlier_than_minute"] )
               if self.globalOptions[ "ends_earlier_than_hour" ] == "12":
                   minTime -= 12*60*60

               if self.globalOptions['ends_earlier_than_ampm'] == "PM":
                   minTime += 60*60*12

               if not courseSection.endsEarlier( minTime ):
                   return False
        except (KeyError, ValueError ), e:
            pass

        return True

    def parseHTML(self, inputHTML):
        soup = BeautifulSoup( inputHTML, convertEntities=BeautifulSoup.HTML_ENTITIES )
        try:
            mainTable = soup.findAll( name="table", limit=1 )[0]
        except IndexError:
            raise QualifierExceptions.CourseMissingException()
        return self.coursesFromTable(mainTable)


    # This function takes html from waterloo and converts it into a course object
    # it is a bit of a mess, but I generally let parsing functions be messy
    def coursesFromTable(self, mainTable):
        courses = []
        for subject in mainTable.findAll( text="Subject" ):
            typeToCourse = {}

            headerRow = subject.findParents( "tr" )[0]
            subjectRow = headerRow.findNextSibling( "tr" )
            details = [e.string.strip() for e in subjectRow.findAll( "td", align="center" )]
            if len( details ) < 2:
                continue


            waterlooCourse = WaterlooCourse()
            waterlooCourse.courseName = "%s %s" % (details[0], details[1] )
            waterlooCourse.courseSubject = cleanString(details[0])
            waterlooCourse.courseCode = cleanString(details[1])
            if len( details ) == 4:
                try:
                    waterlooCourse.creditWorth = float(details[2])
                except ValueError:
                    pass
                waterlooCourse.description = details[3]

            classTable = subjectRow.findNext( "table" )
            classHeaderRow = classTable.findNext( "th" ).parent
            classHeaders = [e.strip().lower() for e in classHeaderRow.findAll( text=re.compile(".*" ) ) if not e.isspace() ]

            classIndex   = classHeaders.index( "class" )
            dateIndex    = classHeaders.index( "time days/date" )
            compSecIndex = classHeaders.index( "comp sec" )
            campusIndex  = classHeaders.index( "camp loc" )
            enrlCapIndex = classHeaders.index( "enrl cap" )
            enrlTotIndex = classHeaders.index( "enrl tot" )

            roomIndex = None
            instructorIndex = None
            rel1Index = None
            rel2Index = None

            try:
                roomIndex = classHeaders.index("bldg room" )
                instructorIndex = classHeaders.index( "instructor" )
            except IndexError:
                pass

            try:
                rel1Index = classHeaders.index("rel 1" )
                rel2Index = classHeaders.index("rel 2" )
            except IndexError:
                pass


            classRows = classHeaderRow.findNextSiblings( "tr" )
            for classRow in classRows:
                tds = classRow.findAll( "td" )

                texts = []
                for td in tds:
                    tdText =  " ".join( cleanString(e) for e in td.contents if type(e) == NavigableString)
                    texts.append(tdText)
                    try:
                        colspan = int(td['colspan'])
                    except KeyError:
                        colspan = 1

                    #Make each row of uniform length, pad with empties
                    if colspan != 1:
                        texts += ["" for x in xrange(colspan -1 )]

                blanks = len( [e for e in texts if not e] )

                if not texts[classIndex] and not texts[compSecIndex]:
                    if lastValid:
                        lastSection = waterlooCourse.sections[-1]
                        if texts[dateIndex]:
                            lastSection.addOfferings(WaterlooCourseOffering.offeringsFromDateString(texts[dateIndex]))
                            lastSection.addDateString(texts[dateIndex])
                        if texts[roomIndex] and texts[roomIndex] != lastSection.room:
                            lastSection.room = "%s / %s" % (lastSection.room, texts[roomIndex])

                elif len(texts) - blanks == 0:
                    #Heuristic - bad row if we are all blank
                    continue
                elif len( classHeaders ) - len( tds ) > 3:
                    #Heuristic - there are more than 3 blank columns
                    continue
                else:
                    lastValid = False

                    #ignore distance ed if we want
                    if not self.globalOptions["show_distance_ed"]:
                        if "DE" in texts[campusIndex] or "Online" in texts[roomIndex]:
                            continue

                    courseSection = WaterlooCourseSection( waterlooCourse )
                    courseSection.uniqueName = texts[classIndex]
                    courseSection.campus = texts[campusIndex]

                    courseType, sectionNum = texts[compSecIndex].split()

                    try:
                        texts[dateIndex].upper().index("TBA")
                        logging.info("Ignoring 'to be announced' %s section %s" % (waterlooCourse.uniqueName, sectionNum))
                        continue
                    except ValueError:
                        pass

                    try:
                        texts[dateIndex].upper().index("CANCEL")
                        logging.info("Ignoring cancelled %s section %s" % (waterlooCourse.uniqueName, sectionNum))
                        continue
                    except ValueError:
                        pass

                    # We have encountered a new "type" in the rows
                    # This may be "LEC" or "TUT". We should check if we have seen it before
                    # and switch the parent of upcoming sections accordingly
                    if not waterlooCourse.type:
                        waterlooCourse.type = courseType
                        typeToCourse[waterlooCourse.type] = waterlooCourse

                    elif waterlooCourse.type != courseType:
                        if courseType in typeToCourse:
                            waterlooCourse = typeToCourse[courseType]
                        else:
                            waterlooCourse = copy.deepcopy(waterlooCourse)
                            waterlooCourse.sections = []
                            waterlooCourse.type = courseType
                            typeToCourse[courseType] = waterlooCourse

                    courseSection.sectionNum = sectionNum
                    courseSection.courseName = waterlooCourse.uniqueName
                    courseSection.alternateName = texts[compSecIndex]
                    courseSection.addOfferings(WaterlooCourseOffering.offeringsFromDateString(texts[dateIndex]))
                    courseSection.addDateString(texts[dateIndex])

                    if enrlTotIndex:
                        try:
                            courseSection.enrlTot = texts[enrlTotIndex]
                        except IndexError:
                            pass
                    if enrlCapIndex:
                        try:
                            courseSection.enrlCap = texts[enrlCapIndex]
                        except IndexError:
                            pass

                    if roomIndex:
                        try:
                            courseSection.room = texts[roomIndex]
                        except IndexError:
                            pass
                    if instructorIndex:
                        try:
                            courseSection.instructor = texts[instructorIndex]
                            courseSection.setRateMyProfessorsInfo()
                        except IndexError:
                            pass
                    if rel1Index and not texts[rel1Index].isspace():
                        try:
                            courseSection.related1 = texts[rel1Index]
                        except IndexError:
                            pass
                    if rel2Index and not texts[rel2Index].isspace():
                        try:
                            courseSection.related2 = texts[rel2Index]
                        except IndexError:
                            pass

                    try:
                        if self.globalOptions["show_full_courses"] == False and courseSection.full():
                            logging.info("Ignoring full section %s section %s" % (waterlooCourse.uniqueName, sectionNum))
                            continue

                    except (KeyError, ValueError), e:
                        pass

                    if not self.meetsTimeOptions(courseSection):
                        continue
                    
                    lastValid = True
                    waterlooCourse.addSection( courseSection ) 

            #Take all courses from the type hash
            courses += [e for e in typeToCourse.values() if self.checkCourseAgainstOptions(e)]

        if len( courses ) == 0:
            raise QualifierExceptions.CourseMissingException()

        self.checkAllCoursesAgainstOptions(courses)

        return courses
