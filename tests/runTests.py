import unittest
import TestWaterlooCourseOffering

def suite():
    load = unittest.defaultTestLoader.loadTestsFromModule
    suite = unittest.TestSuite(map(load, [
            TestWaterlooCourseOffering
        ]))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
