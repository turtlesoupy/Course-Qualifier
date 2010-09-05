import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules" )))

import QualifierExceptions
from WaterlooCourseParser import WaterlooCourseParser

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

class TestWaterlooCourseParser(unittest.TestCase):
    def setUp(self):
        self.math135 = self.loadFileString(os.path.join(DATA_DIR, "math135.htm"))
        self.math136 = self.loadFileString(os.path.join(DATA_DIR, "math136.htm"))
        self.allCourseOptions = {"tutorials": True, "tests": True, "other": True, "sections": []}
        self.noGlobalOptions = {"show_distance_ed": False, "show_full_courses": False}
        self.fullDistanceEdGlobalOptions = {"show_distance_ed": True, "show_full_courses": True}


    def loadFileString(self, pathname):
        f = open(pathname, 'r')
        ret = f.read()
        f.close()
        return ret

    def test_filterMinTime(self):
        globalOptions = self.fullDistanceEdGlobalOptions.copy()
        globalOptions['start_later_than_minute'] = '00'
        globalOptions['start_later_than_hour']   = '12'
        globalOptions['start_later_than_ampm']   = 'PM'

        parser = WaterlooCourseParser(self.allCourseOptions, globalOptions)
        courses = parser.parseHTML(self.math136)
        lecCourses     = [e for e in courses if e.type == "LEC"]
        self.assertEqual(1, len(lecCourses))
        self.assertEqual(2, len(lecCourses[0].sections))

        globalOptions['start_later_than_minute'] = '31'

        parser = WaterlooCourseParser(self.allCourseOptions, globalOptions)
        courses = parser.parseHTML(self.math136)
        lecCourses     = [e for e in courses if e.type == "LEC"]
        self.assertEqual(1, len(lecCourses))
        self.assertEqual(1, len(lecCourses[0].sections))

    def test_filterMaxTime(self):
        globalOptions = self.fullDistanceEdGlobalOptions.copy()
        globalOptions['ends_earlier_than_minute'] = '30'
        globalOptions['ends_earlier_than_hour']   = '1'
        globalOptions['ends_earlier_than_ampm']   = 'PM'

        parser = WaterlooCourseParser(self.allCourseOptions, globalOptions)
        courses = parser.parseHTML(self.math136)
        lecCourses     = [e for e in courses if e.type == "LEC"]
        self.assertEqual(1, len(lecCourses))
        self.assertEqual(2, len(lecCourses[0].sections))

        globalOptions['ends_earlier_than_minute'] = '00'

        parser = WaterlooCourseParser(self.allCourseOptions, globalOptions)
        courses = parser.parseHTML(self.math136)
        lecCourses     = [e for e in courses if e.type == "LEC"]
        self.assertEqual(1, len(lecCourses))
        self.assertEqual(1, len(lecCourses[0].sections))

    def test_filterTypes(self):
        options = self.allCourseOptions.copy()
        parser  = WaterlooCourseParser(options, self.fullDistanceEdGlobalOptions)
        courses = parser.parseHTML(self.math136)
        self.assertEquals(3, len(courses))

        options["tutorials"] = False
        parser  = WaterlooCourseParser(options, self.fullDistanceEdGlobalOptions)
        courses = parser.parseHTML(self.math136)
        self.assertEquals(2, len(courses))

        options["tests"] = False
        parser  = WaterlooCourseParser(options, self.fullDistanceEdGlobalOptions)
        courses = parser.parseHTML(self.math136)
        self.assertEquals(1, len(courses))
        self.assertEquals("LEC", courses[0].type)

    def test_parseFilterFull(self):
        fullParser = WaterlooCourseParser(self.allCourseOptions, self.fullDistanceEdGlobalOptions)
        courses = fullParser.parseHTML(self.math136)
        tutCourses     = [e for e in courses if e.type == "TUT"]
        self.assertEqual(1, len(tutCourses))
        self.assertEqual(3, len(tutCourses[0].sections))


        noFullParser = WaterlooCourseParser(self.allCourseOptions, self.noGlobalOptions)
        courses = noFullParser.parseHTML(self.math136)
        tutCourses     = [e for e in courses if e.type == "TUT"]
        self.assertEqual(1, len(tutCourses))
        self.assertEqual(2, len(tutCourses[0].sections))

    def test_specifyBadSection(self):
        options = self.allCourseOptions.copy()
        options["sections"] = ["ARRR"]
        parser = WaterlooCourseParser(options, self.fullDistanceEdGlobalOptions)
        self.assertRaises(QualifierExceptions.MissingRequiredSectionsException, parser.parseHTML, self.math136)

    def test_specifySections(self):
        options = self.allCourseOptions.copy()
        options["sections"] = []
        parser = WaterlooCourseParser(options, self.fullDistanceEdGlobalOptions)
        courses = parser.parseHTML(self.math136)
        tutCourses     = [e for e in courses if e.type == "TUT"]
        lecCourses     = [e for e in courses if e.type == "LEC"]
        self.assertEqual(1, len(tutCourses))
        self.assertEqual(3, len(tutCourses[0].sections))
        self.assertEqual(1, len(lecCourses))
        self.assertEqual(3, len(lecCourses[0].sections))

        options["sections"] = ["001"]
        parser = WaterlooCourseParser(options, self.fullDistanceEdGlobalOptions)
        courses = parser.parseHTML(self.math136)
        tutCourses     = [e for e in courses if e.type == "TUT"]
        lecCourses     = [e for e in courses if e.type == "LEC"]
        self.assertEqual(1, len(tutCourses))
        self.assertEqual(3, len(tutCourses[0].sections))
        self.assertEqual(1, len(lecCourses))
        self.assertEqual(1, len(lecCourses[0].sections))
        self.assertEqual("001", lecCourses[0].sections[0].sectionNum)

        options["sections"] = ["001", "101"]
        parser = WaterlooCourseParser(options, self.fullDistanceEdGlobalOptions)
        courses = parser.parseHTML(self.math136)
        tutCourses     = [e for e in courses if e.type == "TUT"]
        lecCourses     = [e for e in courses if e.type == "LEC"]
        self.assertEqual(1, len(tutCourses))
        self.assertEqual(1, len(tutCourses[0].sections))
        self.assertEqual("101", tutCourses[0].sections[0].sectionNum)
        self.assertEqual(1, len(lecCourses))
        self.assertEqual(1, len(lecCourses[0].sections))
        self.assertEqual("001", lecCourses[0].sections[0].sectionNum)

    def test_parseIntegrity(self):
        parser = WaterlooCourseParser(self.allCourseOptions, self.fullDistanceEdGlobalOptions)
        courses = parser.parseHTML(self.math135)

        self.assertEquals(3, len(courses))
        
        lectureCourses = [e for e in courses if e.type == "LEC"]
        tutCourses     = [e for e in courses if e.type == "TUT"]
        testCourses    = [e for e in courses if e.type == "TST"]

        self.assertEquals(1, len(lectureCourses))
        self.assertEquals(1, len(tutCourses))
        self.assertEquals(1, len(testCourses))

        lecture  = lectureCourses[0]
        tutorial = tutCourses[0]
        test     = testCourses[0]

        self.assertEquals(10, len(lecture.sections))
        self.assertEquals(2, len(tutorial.sections))
        self.assertEquals(1, len(test.sections))

        self.assertTrue( "201" in  [e.sectionNum for e in test.sections])
        self.assertTrue( "151" in  [e.sectionNum for e in tutorial.sections])
        self.assertTrue( "101" in  [e.sectionNum for e in tutorial.sections])
        self.assertTrue( "005" in  [e.sectionNum for e in lecture.sections])
        self.assertTrue( "001" in  [e.sectionNum for e in lecture.sections])

        #Check section 004 for integrity
        lectureSecs = [e for e in lecture.sections if e.sectionNum == "004"]
        self.assertEqual(1, len(lectureSecs))
        lectureSec = lectureSecs[0]

        self.assertEqual("180", lectureSec.enrlCap)
        self.assertEqual("180", lectureSec.enrlTot)
        self.assertEqual("UW U", lectureSec.campus)
        self.assertEqual("MC 2065", lectureSec.room)
        self.assertEqual("Liu,Yu-Ru", lectureSec.instructor)
        self.assertEqual("5115", lectureSec.uniqueName)






if __name__ == "__main__":
    unittest.main()
