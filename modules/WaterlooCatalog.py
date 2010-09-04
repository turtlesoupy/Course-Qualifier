import os
import sys
import logging
import itertools
from operator import attrgetter
from KeyedObject import KeyedObject


class WaterlooCatalog( object ):
    validMetrics = [
        KeyedObject( "Days of class", "days_full",  "number" ).getJson(),
        KeyedObject( "Time between classes",   "idle_time", "duration"  ).getJson(),
        KeyedObject( "\"Professor Quality\"",    "rmp_quality", "number"  ).getJson(),
        KeyedObject( "Earliest start time", "earliest_start", "time"  ).getJson(),
        KeyedObject( "Latest end time",     "latest_end", "time"  ).getJson(),
        KeyedObject( "Lateness",       "lateness",   "percentage"  ).getJson()
    ]

    def __init__( self, sections ):
        self.sections = sections
        self.metrics = {}

        self.computeMetrics()

    def computeMetrics( self ):
        self.metrics["days_full"] = self.computeValidDays()
        self.metrics["idle_time"] = self.computeIdleTime()
        self.metrics["earliest_start"] = self.computeEarliestStartTime()
        self.metrics["latest_end"] = self.computeLatestEndTime()
        self.metrics["lateness"] = self.computeLateness()
        self.metrics["rmp_quality"] = self.computeRateMyProfessorsQuality()

    #Time in between classes
    def computeIdleTime(self):
        idleTime = 0
        allOfferings  = sorted((itertools.chain(*[e.offerings for e in self.sections])), key=attrgetter('day'))
        for d, g in itertools.groupby(allOfferings, attrgetter('day')):
            sortedDay = sorted(g, lambda x,y : x.startTime - y.startTime)
            for i in xrange(len(sortedDay) - 1):
                idleTime += sortedDay[i+1].startTime - sortedDay[i].endTime
        return idleTime
    
    def computeRateMyProfessorsQuality(self):
        rmpRatings = [e.rateMyProfessorsQuality for e in self.sections if e.rateMyProfessorsQuality != None]
        if len(rmpRatings) == 0:
            return None
        else:
            return float(sum(rmpRatings)) / len(rmpRatings)

    def computeValidDays(self):
        return len(set(o.day for o in itertools.chain(*[e.offerings for e in self.sections])))

    def computeEarliestStartTime(self):
        return min(o.startTime for o in itertools.chain(*[e.offerings for e in self.sections]))

    def computeLatestEndTime(self):
        return max(o.endTime for o in itertools.chain(*[e.offerings for e in self.sections]))

    def computeLateness(self):
        maxTime = 24*60*60 * sum(len(e.offerings) for e in self.sections)
        if maxTime <= 0:
            return 0

        myTime = sum(o.endTime for o in itertools.chain(*[e.offerings for e in self.sections]))
        return float(myTime) / maxTime

    def getJson( self, reference=True ):
        if reference:
            sections = [e.getReferenceJson() for e in self.sections]
        else:
            sections = [e.getJson() for e in self.sections]

        return { 
            "metrics" : self.metrics,
            "sections" : sections 
        }
