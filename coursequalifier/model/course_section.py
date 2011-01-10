import re
import copy
import string
import logging
from course_offering import CourseOffering

class CourseSection(object):
    c_date_map = { "M": 1, "T": 2, "W": 3, "Th": 4, "F": 5, "S": 6 }
    c_date_re = re.compile( "(\d{2}):(\d{2})-(\d{2}):(\d{2})(\w+)" )
    @classmethod
    def fromDataJson(cls, json, courseName):
        sec = CourseSection()
        grabs = [
            ('classNumber', 'class_number'),
            ('campus',   'campus_location'),
            ('building', 'building'),
            ('room',     'room'),
            ('enrlCap',  'enrollment_cap'),
            ('enrlTot',  'enrollment_total'),
            ('related1', 'related_component_1'),
            ('related2', 'related_component_2'),
            ('instructor', 'instructor'),
            ('instructorId', 'instructor_id')
        ]

        for (k, jk) in grabs:
            if jk in json:
                setattr(sec, k, json[jk])
        
        startTimeInt = int(json['start_time'])
        endTimeInt   = int(json['end_time'])
 
        startHours   = startTimeInt / 100
        endHours     = endTimeInt   / 100
        startMinutes = startTimeInt % 100
        endMinutes   = endTimeInt   % 100


        sec.addOfferings(CourseOffering.offeringsFromDaysAndTime(
            json['days'], startHours * 60 * 60 + startMinutes * 60,
            endHours * 60 * 60 + endMinutes * 60)) 

        sec.dateString = CourseOffering.displayString(sec.offerings)
        sec.courseName = courseName
        sec.sectionNum = " ".join(json["component_section"].split()[1:])

        return sec

    def __init__(self, parent=None):
        self.parent = parent
        self.courseName = ""
        self.classNumber = ""
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
        return hash(self.classNumber + self.courseName)


    def addOfferings(self, newOfferings):
        self.offerings += newOfferings
        self.offerings = CourseOffering.uniqueOfferings(self.offerings) #Removes weird parse errors
        self.hasValidDate = len(self.offerings) > 0

    def addDateString(self, dateStr):
        self.dateString = ("%s %s" % (self.dateString, dateStr)).strip()

    def full(self):
        if self.enrlCap == -1 or self.enrlTot == -1:
            return False

        return self.enrlTot >= self.enrlCap

    def conflictsWith( self, otherSection ):
        for o1 in self.offerings:
            if any(o1.conflictsWith(o2) for o2 in otherSection.offerings):
                return True

        return False

    def startsAfter(self, time):
        return all(o.startTime >= time for o in self.offerings)

    def endsBefore(self, time):
        return all(o.endTime < time for o in self.offerings)

    @property
    def buildingRoom(self):
        if self.building and self.room:
            return "%s %s" % (self.building, self.room)
        else:
            return ""
