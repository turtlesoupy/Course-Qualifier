import os
import sys

rateMyProfessorsDatabase = os.path.abspath(
        os.path.join( 
            os.path.abspath( os.path.dirname( __file__ )),
            "../databases/rate_my_professors.db" ) )

waterlooStatistics= os.path.abspath(
        os.path.join( 
            os.path.abspath( os.path.dirname( __file__ )),
            "../databases/waterloo_statistics.db" ) )

statisticsDbs = [("waterloo", waterlooStatistics) ]
