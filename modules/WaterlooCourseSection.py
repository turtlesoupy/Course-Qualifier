import re
import copy
import logging
import simplejson
from KeyedObject import KeyedObject
import QualifierExceptions

class WaterlooCourseSection:
    c_date_map = { "M": 1, "T": 2, "W": 3, "Th": 4, "F": 5, "S": 6 }
    c_date_re = re.compile( "(\d{2}):(\d{2})-(\d{2}):(\d{2})(\w+)" )
    sectionInformation = [
        KeyedObject( "Section Number", "section_num").getJson(),
        KeyedObject( "Catalog Number", "unique_name").getJson(),
        KeyedObject( "Time(s)", "date_string").getJson(),
        KeyedObject( "Room", "room" ).getJson(),
        KeyedObject( "Instructor", "instructor" ).getJson()
    ]

    def __init__( self, parent ):
        self.parent = parent
        self.courseName = ""
        self.uniqueName = ""
        self.instructor = ""
        self.room = ""
        self.campus = ""
        self.sectionNum = ""
        self.related1 = ""
        self.related2 = ""
        self.enrlCap = -1
        self.enrlTot = -1
        self.hasValidDate = False
        self.offerings  = []
        self.dateString = ""

    def __hash__( self ):
        return hash(self.uniqueName + self.courseName)


    def addOfferings(self, newOfferings):
        self.offerings += newOfferings
        self.hasValidDate = len(self.offerings) > 0

    def addDateString(self, dateStr):
        self.dateString = ("%s %s" % (self.dateString, dateStr)).strip()


    def full( self ):
        if self.enrlCap == -1 or self.enrlTot == -1:
            return False

        return self.enrlTot >= self.enrlCap

    def conflictsWith( self, otherSection ):
        for o1 in self.offerings:
            if any(o1.conflictsWith(o2) for o2 in otherSection.offerings):
                return True

        return False

    def startsAfter( self, time ):
        return not any(o.startTime < time for o in self.offerings)

    def endsEarlier( self, time ):
        return not any(o.endTime > time for o in self.offerings)

    def getReferenceJson( self ):
        return {
                    "courseName": self.courseName,
                    "sectionName": self.uniqueName
                }

    def jsonDump( self ):
        return simplejson.dumps( self.getJson() )

    def dump( self ):
        return """WaterlooCourseSection: %(name)s Instructor:'%(instructor)s' Room:'%(room)s' valid:'%(times)s""" % \
                {"name": self.uniqueName, "instructor": self.instructor, "room": self.room}

    def getJson( self ):
        return {  "unique_name": self.uniqueName,
                "section_num": self.sectionNum,
                "instructor": self.instructor,
                "room": self.room,
                "campus": self.campus,
                "offerings":   [e.getJson() for e in self.offerings],
                "related1" : self.related1,
                "related2" : self.related2,
                "date_string" : self.dateString
            } 
