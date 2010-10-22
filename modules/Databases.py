import os
import sys

waterlooStatistics= os.path.abspath(
        os.path.join( 
            os.path.abspath( os.path.dirname( __file__ )),
            "../databases/waterloo_statistics.db" ) )

statisticsDbs = [("waterloo", waterlooStatistics) ]
