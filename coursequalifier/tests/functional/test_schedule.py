from coursequalifier.tests import *

class TestScheduleController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='schedule', action='index'))
        # Test response...
