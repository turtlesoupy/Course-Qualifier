import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules" )))

from WaterlooCourse import WaterlooCourse
from WaterlooCourseOffering import WaterlooCourseOffering
from WaterlooCourseSection import WaterlooCourseSection

class TestWaterlooCourseSection(unittest.TestCase):
    def setUp(self):
        self.dummyCourse = WaterlooCourse()

    def test_full(self):
        emptySec = WaterlooCourseSection(self.dummyCourse)
        emptySec.enrlCap = -1 
        emptySec.enrlTot = -1 

        self.assertTrue(not emptySec.full())
        emptySec.enrlCap =  80
        self.assertTrue(not emptySec.full())
        emptySec.enrlTot = 15
        self.assertTrue(not emptySec.full())
        emptySec.enrlTot = 80
        self.assertTrue(emptySec.full())
        emptySec.enrlTot = 81
        self.assertTrue(emptySec.full())

    def test_conflictsWith(self):
        sec1 = WaterlooCourseSection(self.dummyCourse)
        sec2 = WaterlooCourseSection(self.dummyCourse)

        self.assertTrue(not sec1.conflictsWith(sec2))
        sec1.addOfferings(WaterlooCourseOffering.offeringsFromDateString("11:30-12:50TTh"))
        self.assertTrue(not sec1.conflictsWith(sec2))
        sec2.addOfferings(WaterlooCourseOffering.offeringsFromDateString("11:30-12:50M"))
        self.assertTrue(not sec1.conflictsWith(sec2))
        sec2.addOfferings(WaterlooCourseOffering.offeringsFromDateString("11:50-12:20Th"))
        self.assertTrue(sec1.conflictsWith(sec2))

    def test_startsAfter(self):
        sec = WaterlooCourseSection(self.dummyCourse)
        self.assertTrue(sec.startsAfter(12*60*60))
        sec.addOfferings(WaterlooCourseOffering.offeringsFromDateString("11:30-12:50TTh"))
        self.assertTrue(not sec.startsAfter(12*60*60))
        self.assertTrue(sec.startsAfter(11*60*60))

    def test_endsEarlier(self):
        sec = WaterlooCourseSection(self.dummyCourse)
        self.assertTrue(sec.endsEarlier(12*60*60))
        sec.addOfferings(WaterlooCourseOffering.offeringsFromDateString("11:30-12:50TTh"))
        self.assertTrue(not sec.endsEarlier(12*60*60))
        self.assertTrue(sec.endsEarlier(13*60*60))

if __name__ == "__main__":
    unittest.main()
