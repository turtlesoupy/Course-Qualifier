import unittest
import TestWaterlooCourseOffering
import TestWaterlooCourseParser
import TestWaterlooCourseSection
import TestWaterlooCatalog
import TestWaterlooDispatcher

def suite():
    load = unittest.defaultTestLoader.loadTestsFromModule
    suite = unittest.TestSuite(map(load, [
            TestWaterlooCourseOffering,
            TestWaterlooCourseParser,
            TestWaterlooCourseSection,
            TestWaterlooCatalog,
            TestWaterlooDispatcher
        ]))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
