import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules" )))

import QualifierExceptions
from WaterlooCatalog import WaterlooCatalog
from WaterlooCourse import WaterlooCourse
from WaterlooCourseSection import WaterlooCourseSection
from WaterlooCourseOffering import WaterlooCourseOffering
from WaterlooDispatcher import WaterlooDispatcher, TOO_MANY_COMBINATIONS

class TestWaterlooDispatcher(unittest.TestCase):
    def setUp(self):
        self.dummyRequest = {
                    "options": {},
                    "courses": [],
                    "term":    1011
                }

        self.dummyCourse = WaterlooCourse()

    def test_qualifyCourses(self):
        dispatcher = WaterlooDispatcher(self.dummyRequest)
        course1 = WaterlooCourse()
        course2 = WaterlooCourse()
        courses = [course1, course2]
        dispatcher.qualifiedSectionList = []
        dispatcher.qualifyCourses(courses)
        self.assertEqual([], dispatcher.qualifiedSectionList)

        course1Sec1= WaterlooCourseSection(course1)
        course1Sec1.addOfferings(WaterlooCourseOffering.offeringsFromDateString("11:30-12:20MWF"))
        course1.sections = [course1Sec1]
        dispatcher.qualifiedSectionList = []
        dispatcher.qualifyCourses(courses[:])
        self.assertEqual([[course1Sec1]], dispatcher.qualifiedSectionList)


        course1Sec2= WaterlooCourseSection(course1)
        course1Sec2.addOfferings(WaterlooCourseOffering.offeringsFromDateString("11:30-12:20TTh"))
        course1.sections = [course1Sec1, course1Sec2]
        dispatcher.qualifiedSectionList = []
        dispatcher.qualifyCourses(courses[:])
        self.assertEqual([[course1Sec1], [course1Sec2]], dispatcher.qualifiedSectionList)

        course2Sec1= WaterlooCourseSection(course1)
        course2Sec1.addOfferings(WaterlooCourseOffering.offeringsFromDateString("11:40-12:20T"))
        course2.sections = [course2Sec1]
        courses = [course1, course2]
        dispatcher.qualifiedSectionList = []
        dispatcher.qualifyCourses(courses[:])
        self.assertEqual(1, len(dispatcher.qualifiedSectionList))
        self.assertEqual(2, len(dispatcher.qualifiedSectionList[0]))
        self.assertTrue(course1Sec1 in dispatcher.qualifiedSectionList[0])
        self.assertTrue(course2Sec1 in dispatcher.qualifiedSectionList[0])

    def test_checkBlowup(self):
        dispatcher = WaterlooDispatcher(self.dummyRequest)
        course1 = WaterlooCourse()
        course2 = WaterlooCourse()
        try:
            dispatcher.checkBlowup([course1, course2], [])
            self.assertTrue(True)
        except QualifierExceptions.TooManySchedulesException:
            self.assertTrue(False)
        
        course1.sections = [None] * (TOO_MANY_COMBINATIONS + 1) 
        self.assertRaises(QualifierExceptions.TooManySchedulesException, dispatcher.checkBlowup, [course1, course2], [])
        course1.sections = course1.sections[5:]
        course2.sections = [None, None]
        self.assertRaises(QualifierExceptions.TooManySchedulesException, dispatcher.checkBlowup, [course1, course2], [])


if __name__ == "__main__":
    unittest.main()
