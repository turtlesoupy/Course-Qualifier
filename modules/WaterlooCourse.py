import re
import copy
import logging
import simplejson
import QualifierExceptions
from KeyedObject import KeyedObject
from WaterlooCourseSection import WaterlooCourseSection

class WaterlooCourse:
    def __init__( self ):
        self.courseName = ""
        self.alternateName = ""
        self.description = ""
        self.creditWorth = 0
        self.sections = []
        self.type = ""

    @property
    def uniqueName(self):
        return "%s %s" % (self.courseName, self.type )

    def dump( self ):
        return """WaterlooCourse: %(name)s (%(desc)s)""" % \
                {"name": self.uniqueName, "desc": self.description}

    def getJson( self ):
        return   {
                    "courseName": self.uniqueName,
                    "type": self.type,
                    "description": self.description,
                    "sections": dict( (e.uniqueName, e.getJson()) for e in self.sections ),
                    }



    def jsonDump( self ):
        return simplejson.dumps( self.getJson() )


    def addSection( self, section ):
        self.sections.append( section )
