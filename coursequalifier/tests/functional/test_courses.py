from coursequalifier.tests import *

class TestCoursesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='courses', action='index'))
        # Test response...
