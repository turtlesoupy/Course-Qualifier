import os
import ConfigParser

class QualifierConfig(object):
    def readConfig(self, stream):
        config = ConfigParser.ConfigParser()
        config.readfp(stream)

        self.uwdataAddress = config.get("Qualifier", "uwdataAddress")
        self.uwdataKey     = config.get("Qualifier", "uwdataKey")

config = QualifierConfig()

defaultPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/qualifier.cfg")
def readDefault(path=defaultPath):
    with open(path,'r') as f:
        config.readConfig(f)

"""Global configuration object."""
