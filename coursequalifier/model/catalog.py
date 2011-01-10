import os
import sys
import logging
import itertools
from operator import attrgetter

def cartesian(*args):
    ans = [[]]
    for arg in args:
        ans = [x+[y] for x in ans for y in arg]
    return ans

class CatalogCombinatorics(object):
    """Algorithm-object for doing actual 'course qualifying'."""
    def __init__(self, direct, searchGroups):
        self.direct       = direct
        self.searchGroups = searchGroups
        self.output       = []

    def computeSections(self):
        self.computeInternal(self.direct)
        self.computeSearchCourses()

    def computeSearchCourses(self):
        if len(self.searchGroups) <= 0:
            return

        directCatalogs = self.output[:]
        self.output    = []

        searchList = cartesian(*self.searchGroups)
        for searchables in searchList:
            possibleCourses = []
            for classGroup in searchables:
                possibleCourses.extend(classGroup)

            if len(directCatalogs) == 0:
                self.computeInternal(possibleCourses, []) #Side effect!
            else:
                for catalog in directCatalogs:
                    self.computeInternal(possibleCourses[:], catalog[:]) #Side effect!

    def computeInternal(self, remainingCourses, sectionAcc=[]):
        if len(remainingCourses) == 0:
            if len(sectionAcc) > 0: #and self.checkCatalog(sectionAcc):
                self.output.append(sectionAcc)
        else:
            currentCourse = remainingCourses.pop()
            for currSection in currentCourse.sections:
                for otherSection in sectionAcc:
                    if currSection.conflictsWith(otherSection):
                        #self.conflictingSections.add((currSection, otherSection))
                        break
                else:
                    self.computeInternal(remainingCourses[:], sectionAcc[:] + [currSection])

class Catalog(object):
    @classmethod
    def computeAll(cls, directCourses, searchGroups):
        c = CatalogCombinatorics(directCourses, searchGroups)
        c.computeSections()
        return [cls(e) for e in c.output]

    def __init__(self, sections):
        self.sections = sections
        self.metrics = {}
        self.computeMetrics()

    def computeMetrics( self ):
        self.metrics["days_full"] = self.computeDaysFull()
        self.metrics["idle_time"] = self.computeIdleTime()
        self.metrics["earliest_start"] = self.computeEarliestStartTime()
        self.metrics["latest_end"] = self.computeLatestEndTime()
        self.metrics["lateness"] = self.computeLateness()

    #Time in between classes
    def computeIdleTime(self):
        idleTime = 0
        allOfferings  = sorted((itertools.chain(*[e.offerings for e in self.sections])), key=attrgetter('day'))
        for d, g in itertools.groupby(allOfferings, attrgetter('day')):
            sortedDay = sorted(g, lambda x,y : x.startTime - y.startTime)
            for i in xrange(len(sortedDay) - 1):
                idleTime += sortedDay[i+1].startTime - sortedDay[i].endTime
        return idleTime
    
    def computeDaysFull(self):
        return len(set(o.day for o in itertools.chain(*[e.offerings for e in self.sections])))

    def computeEarliestStartTime(self):
        try:
            return min(o.startTime for o in itertools.chain(*[e.offerings for e in self.sections]))
        except ValueError:
            return None

    def computeLatestEndTime(self):
        try:
            return max(o.endTime for o in itertools.chain(*[e.offerings for e in self.sections]))
        except ValueError:
            return None

    def computeLateness(self):
        maxTime = 24*60*60 * sum(len(e.offerings) for e in self.sections)
        if maxTime <= 0:
            return 0

        myTime = sum(o.endTime for o in itertools.chain(*[e.offerings for e in self.sections]))
        return float(myTime) / maxTime
