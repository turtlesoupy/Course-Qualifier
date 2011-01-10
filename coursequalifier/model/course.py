import re
import copy
import logging
import itertools
from course_section import CourseSection
import coursequalifier.lib.uwdata as uwdata

class Course(object):
    @classmethod
    def coursesFromCode(cls, acronym, code, term, courseJson=None, sectionFilters=[]):
        if courseJson == None:
            courseJson  = uwdata.pullCourseInfo(acronym, code)

        sectionJson = uwdata.pullSectionInfo(acronym, code, term)["classes"]

        keyfun = lambda x: x["class"]["component_section"].split()[0]
        sectionJson = sorted(sectionJson, key=keyfun)
        courses = []

        for k, g in itertools.groupby(sectionJson, keyfun):
            typedCourse = cls.fromDataJson(courseJson['course'])
            typedCourse.type = k
            potentialSections = [CourseSection.fromDataJson(e['class'], typedCourse.uniqueName)  for e in g]

            typedCourse.sections = [e for e in potentialSections \
                                    if all(sectionFilter.passes(e) for sectionFilter in sectionFilters)]
            courses.append(typedCourse)

        return courses

    @classmethod
    def courseGroupsFromSearch(cls, query, term, sectionFilters=[]):
        searchJson   = uwdata.pullSearchCourses(query) 
        courseGroups = [cls.coursesFromCode(e['course']["faculty_acronym"], 
            e['course']["course_number"], term, e, sectionFilters) for e in searchJson["courses"]]

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

    def addSection( self, section ):
        self.sections.append( section )

