import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules" )))

from WaterlooCourseOffering import WaterlooCourseOffering, WaterlooWeeklyOffering

class TestWaterlooCourseOffering(unittest.TestCase):
    def test_badOfferingsFromDateString(self):
        self.assertEqual([], WaterlooCourseOffering.offeringsFromDateString("vfsklgfng"))
        self.assertEqual([], WaterlooCourseOffering.offeringsFromDateString(""))
        self.assertEqual([], WaterlooCourseOffering.offeringsFromDateString("22:111"))
        self.assertEqual([], WaterlooCourseOffering.offeringsFromDateString("22:11"))
        self.assertEqual([], WaterlooCourseOffering.offeringsFromDateString("22:11PM"))
        self.assertEqual([], WaterlooCourseOffering.offeringsFromDateString("11:30-12:50"))

    def test_offeringsFromDateString(self):
        tuesThurs = WaterlooCourseOffering.offeringsFromDateString("11:30-12:50TTh")
        expectedStart = 11*60*60 + 30*60
        expectedEnd   = 12*60*60 + 50*60
        self.assertEqual(2, len(tuesThurs))
        self.assertEqual(WaterlooWeeklyOffering.TUESDAY, tuesThurs[0].day)
        self.assertEqual(WaterlooWeeklyOffering.THURSDAY, tuesThurs[1].day)
        self.assertEqual(expectedStart, tuesThurs[0].startTime)
        self.assertEqual(expectedStart, tuesThurs[1].startTime)
        self.assertEqual(expectedEnd, tuesThurs[0].endTime)
        self.assertEqual(expectedEnd, tuesThurs[1].endTime)

    def test_offeringsFromDateStringAmbiguous(self):
        offerings = WaterlooCourseOffering.offeringsFromDateString("08:30-09:30M")
        self.assertEqual(1, len(offerings))
        self.assertEqual(8*60*60 + 30*60, offerings[0].startTime)
        self.assertEqual(9*60*60 + 30*60, offerings[0].endTime)

        offerings = WaterlooCourseOffering.offeringsFromDateString("07:30-09:30M")
        self.assertEqual(1, len(offerings))
        self.assertEqual(19*60*60 + 30*60, offerings[0].startTime)
        self.assertEqual(21*60*60 + 30*60, offerings[0].endTime)


class TestWaterlooWeeklyOffering(unittest.TestCase):
    def setup(self):
        pass

    def test_conflictsWithSameDay(self):
        one = WaterlooWeeklyOffering(WaterlooWeeklyOffering.MONDAY, 0, 100)
        two = WaterlooWeeklyOffering(WaterlooWeeklyOffering.MONDAY, 0, 100)
        self.assertTrue(one.conflictsWith(two))
        self.assertTrue(two.conflictsWith(one))

    def test_conflictsWithDifferentDay(self):
        one = WaterlooWeeklyOffering(WaterlooWeeklyOffering.MONDAY, 0, 100)
        two = WaterlooWeeklyOffering(WaterlooWeeklyOffering.TUESDAY, 0, 100)
        self.assertTrue(not one.conflictsWith(two))
        self.assertTrue(not two.conflictsWith(one))

    def test_conflictsWithOverlap(self):
        one = WaterlooWeeklyOffering(WaterlooWeeklyOffering.MONDAY, 0, 100)
        two = WaterlooWeeklyOffering(WaterlooWeeklyOffering.MONDAY, 50, 150)
        self.assertTrue(one.conflictsWith(two))
        self.assertTrue(two.conflictsWith(one))

    def test_conflictsWithNoOverlap(self):
        one = WaterlooWeeklyOffering(WaterlooWeeklyOffering.MONDAY, 0, 100)
        two = WaterlooWeeklyOffering(WaterlooWeeklyOffering.MONDAY, 101, 200)
        self.assertTrue(not one.conflictsWith(two))
        self.assertTrue(not two.conflictsWith(one))

if __name__ == "__main__":
    unittest.main()
