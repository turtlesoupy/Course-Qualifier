import re
import copy
import logging
import itertools
import simplejson
import QualifierExceptions
from KeyedObject import KeyedObject
from WaterlooCourseSection import WaterlooCourseSection
import WaterlooData

class WaterlooCourse:
    @classmethod
    def coursesFromCode(cls, acronym, code, term, courseJson=None):
        if courseJson == None:
            courseJson  = WaterlooData.pullCourseInfo(acronym, code)

        sectionJson = WaterlooData.pullSectionInfo(acronym, code, term)["classes"]

        keyfun = lambda x: x["class"]["component_section"].split()[0]
        sectionJson = sorted(sectionJson, key=keyfun)
        courses = []

        for k, g in itertools.groupby(sectionJson, keyfun):
            typedCourse = cls.fromDataJson(courseJson['course'])
            typedCourse.type = k
            typedCourse.sections = [WaterlooCourseSection.fromDataJson(e['class'], typedCourse.uniqueName) for e in g]
            courses.append(typedCourse)

        return courses

    @classmethod
    def coursesFromSearch(cls, query, term):
        searchJson   = WaterlooData.pullSearchCourses(query) 
        courseGroups = [cls.coursesFromCode(e['course']["faculty_acronym"], 
            e['course']["course_number"], term, e) for e in searchJson["courses"]]

        return [g for g in courseGroups if len(g) > 0]

    @classmethod
    def fromDataJson(cls, json):
        directJsons = [
            ('courseSubject', 'faculty_acronym'),
            ('courseCode',    'course_number'),
            ('description',   'description'),
            ('calendarUrl',   'src_url'),
            ('title',         'title')
        ]

        course = cls()
        for k, jk in directJsons:
            if jk in json:
                setattr(course, k, json[jk])

        course.courseName = "%s %s" % (course.courseSubject, course.courseCode)

        return course

    def __init__( self ):
        self.courseName    = "" #Subject + Code
        self.courseSubject = ""
        self.courseCode    = ""
        self.alternateName = ""
        self.description   = ""
        self.creditWorth   = 0
        self.sections      = []
        self.type = ""

    @property
    def uniqueName(self):
        return "%s %s" % (self.courseName, self.type)

    def dump( self ):
        return """WaterlooCourse: %(name)s (%(desc)s)""" % \
                {"name": self.uniqueName, "desc": self.description}

    def getJson( self ):
        return   {
                    "courseName": self.uniqueName,
                    "type": self.type,
                    "description": self.description,
                    "title": self.title,
                    "sections": dict((e.classNumber, e.getJson()) for e in self.sections),
                    }



    def jsonDump( self ):
        return simplejson.dumps( self.getJson() )


    def addSection( self, section ):
        self.sections.append( section )
