import os
import sys
import logging
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
        
        #Valid days
        validDays = [False]*7
        for section in self.sections:
            for i, dayTime in enumerate( section.validTimes ):
                for times in dayTime:
                    if times[0] and times[1]:
                        validDays[i] = True

        numValidDays = len( [e for e in validDays if e]  )
        self.metrics["days_full"] = numValidDays
        
        #Time between classes
        timesPerDay = [None]*7
        for section in self.sections:
            for i, dayTimes in enumerate( section.validTimes ):
                for times in dayTimes:
                    if times[0] and times[1]:
                        if not timesPerDay[i]:
                            timesPerDay[i] = []
                        timesPerDay[i].append( times )

        idleTime = 0
        for day in (e for e in timesPerDay if e):
            day.sort( lambda x, y: x[0] - y[0] )
            for i in range( len( day ) - 1):
                idleTime += day[i+1][0] - day[i][1]

        self.metrics["idle_time"] = idleTime 

        #Earliest start time / Latest end time
        earliestStart = None
        latestEnd = None

        for section in self.sections:
            for dayTimes in section.validTimes:
                for start, end in dayTimes:
                    if not earliestStart and not latestEnd:
                        earliestStart = start
                        latestEnd = end
                    else:
                        if start and start < earliestStart:
                            earliestStart = start
                        if end and end > latestEnd:
                            latestEnd = end

        self.metrics["earliest_start"] = earliestStart
        self.metrics["latest_end"] = latestEnd


        #Rate my professors quality
        rmp_sections = 0
        rmp_quality = 0.0
        for section in self.sections:
            if section.rateMyProfessorsQuality != None:
                rmp_sections += 1
                rmp_quality += section.rateMyProfessorsQuality

        if rmp_sections > 0:
            self.metrics["rmp_quality"] = rmp_quality / rmp_sections
        else:
            self.metrics["rmp_quality"] = None

        self.setLateness()

    def setLateness(self):
        maximumTime = 24*60*60 * sum( sum([ len(dayTime) for dayTime in e.validTimes]) for e in self.sections )
        realTime =  sum( sum( sum(x[1] for x in dayTime) for dayTime in e.validTimes) for e in self.sections )
	if maximumTime == 0:
		self.metrics["lateness"] = 0
	else:
		self.metrics["lateness"] = float(realTime) / maximumTime
         

    def getJson( self, reference=True ):
        if reference:
            sections = [e.getReferenceJson() for e in self.sections]
        else:
            sections = [e.getJson() for e in self.sections]

        return { 
            "metrics" : self.metrics,
            "sections" : sections 
        }
