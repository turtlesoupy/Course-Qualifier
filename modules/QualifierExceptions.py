class QualifierException(RuntimeError):
    def getJson( self ):
        return { 
            "name"   : self.__class__.__name__,
            "string" : str(self )
            }

class TooManySchedulesException( QualifierException ):
    def __init__( self, numClasses ):
        self.numClasses = numClasses

    def getJson( self ):
        return { "name" : self.__class__.__name__,
                 "numClasses" : self.numClasses }

class InvalidInput( QualifierException ):
    pass

class MissingRequiredSectionsException( QualifierException ):
    pass

class CourseMissingException(QualifierException):
    pass

class FailedPrecheckException( QualifierException ):
    pass
