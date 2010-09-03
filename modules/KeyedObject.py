import os
import sys

class KeyedObject( object ):
    def __init__( self, name, key, type="text"):
        self.name = name
        self.key = key
        self.type = type

    def getJson(self ):
        return {
            "name": self.name,
            "key" : self.key,
            "type" : self.type
        }
