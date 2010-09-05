import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules" )))

from WaterlooCatalog import WaterlooCatalog
from WaterlooCourse import WaterlooCourse
from WaterlooCourseSection import WaterlooCourseSection
from WaterlooCourseOffering import WaterlooCourseOffering

class TestWaterlooCatalog(unittest.TestCase):
    def setUp(self):
        self.dummyCourse = WaterlooCourse()

    def test_computeIdleTime(self):
        sec1 = WaterlooCourseSection(self.dummyCourse)
        sec2 = WaterlooCourseSection(self.dummyCourse)
        catalog = WaterlooCatalog([sec1, sec2])
        self.assertEqual(0, catalog.computeIdleTime())
        sec1.addOfferings(WaterlooCourseOffering.offeringsFromDateString("11:30-12:50TTh"))
        self.assertEqual(0, catalog.computeIdleTime())
        sec2.addOfferings(WaterlooCourseOffering.offeringsFromDateString("13:00-14:00T"))
        self.assertEqual(10*60, catalog.computeIdleTime())
        sec2.addOfferings(WaterlooCourseOffering.offeringsFromDateString("17:00-17:50T"))
        self.assertEqual(10*60 + 3*60*60, catalog.computeIdleTime())

    def test_computeRateMyProfessorsQuality(self):
        sec1 = WaterlooCourseSection(self.dummyCourse)
        sec2 = WaterlooCourseSection(self.dummyCourse)
        catalog = WaterlooCatalog([sec1, sec2])
        self.assertEqual(None, catalog.computeRateMyProfessorsQuality())
        sec1.rateMyProfessorsQuality = 4.0
        self.assertEqual(4.0, catalog.computeRateMyProfessorsQuality())
        sec2.rateMyProfessorsQuality = 2.0
        self.assertEqual(3.0, catalog.computeRateMyProfessorsQuality())

    def test_computeDaysFull(self):
        sec1 = WaterlooCourseSection(self.dummyCourse)
        sec2 = WaterlooCourseSection(self.dummyCourse)
        catalog = WaterlooCatalog([sec1, sec2])
        self.assertEqual(0, catalog.computeDaysFull())
        sec1.addOfferings(WaterlooCourseOffering.offeringsFromDateString("11:30-12:50TTh"))
        self.assertEqual(2, catalog.computeDaysFull())
        sec2.addOfferings(WaterlooCourseOffering.offeringsFromDateString("13:00-14:00T"))
        self.assertEqual(2, catalog.computeDaysFull())
        sec2.addOfferings(WaterlooCourseOffering.offeringsFromDateString("13:00-14:00W"))
        self.assertEqual(3, catalog.computeDaysFull())

    def test_computeEarliestStartTime(self):
        sec1 = WaterlooCourseSection(self.dummyCourse)
        sec2 = WaterlooCourseSection(self.dummyCourse)
        catalog = WaterlooCatalog([sec1, sec2])
        self.assertEqual(None, catalog.computeEarliestStartTime())
        sec1.addOfferings(WaterlooCourseOffering.offeringsFromDateString("11:30-12:50TTh"))
        self.assertEqual(11 * 60*60 + 30*60, catalog.computeEarliestStartTime())
        sec2.addOfferings(WaterlooCourseOffering.offeringsFromDateString("11:00-12:50T"))
        self.assertEqual(11 * 60*60, catalog.computeEarliestStartTime())
        sec1.addOfferings(WaterlooCourseOffering.offeringsFromDateString("10:00-10:50M"))
        self.assertEqual(10 * 60*60, catalog.computeEarliestStartTime())

    def test_computeLatestEndTime(self):
        sec1 = WaterlooCourseSection(self.dummyCourse)
        sec2 = WaterlooCourseSection(self.dummyCourse)
        catalog = WaterlooCatalog([sec1, sec2])
        self.assertEqual(None, catalog.computeLatestEndTime())
        sec1.addOfferings(WaterlooCourseOffering.offeringsFromDateString("11:30-12:50TTh"))
        self.assertEqual(12 * 60*60 + 50*60, catalog.computeLatestEndTime())
        sec2.addOfferings(WaterlooCourseOffering.offeringsFromDateString("11:00-12:55T"))
        self.assertEqual(12 * 60*60 + 55*60, catalog.computeLatestEndTime())
        sec1.addOfferings(WaterlooCourseOffering.offeringsFromDateString("10:00-10:50M"))
        self.assertEqual(12 * 60*60 + 55*60, catalog.computeLatestEndTime())


if __name__ == "__main__":
    unittest.main()
