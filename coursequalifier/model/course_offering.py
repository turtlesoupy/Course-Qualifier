import os
import re
import sys
import logging
import itertools
from operator import attrgetter

def secondsToTime(seconds):
    hours = seconds / 3600
    seconds -= 3600*hours
    minutes = seconds / 60
    return "%02d:%02d" % (hours, minutes)

# This class can be expanded to include biweekly offerings
class CourseOffering(object):
    dateRE = re.compile( "(\d{2}):(\d{2})-(\d{2}):(\d{2})(\w+)" )

    @classmethod
    def uniqueOfferings(cls, offerList):
        ret = []
        for o1 in offerList:
            for o2 in ret:
                if o1.day == o2.day and o1.startTime == o2.startTime and o1.endTime == o2.endTime:
                    break
            else:
                ret.append(o1)

        return ret

    @classmethod
    def displayString(cls, offerList):
        displays = []
        offerSort = sorted(offerList, key=attrgetter("__class__"))
        for k,g in itertools.groupby(offerSort, key=attrgetter("__class__")):
            groups = list(g)
            displays.append(groups[0].displayString(groups))

        return ", ".join(displays)

    @classmethod
    def offeringsFromDaysAndTime(cls, days, startTime, endTime):
        #Hacky parse to differentiate "Th" and "T"
        curDay = days[0]
        validDays = []
        for char in days[1:]:
            if curDay and char.isupper():
                validDays.append( curDay )
                curDay = char
            else:
                curDay += char

        validDays.append(curDay)

        return [WeeklyOffering(
            WeeklyOffering.STRING_TO_DAY[day], 
            startTime, endTime) for day in validDays \
                    if day in WeeklyOffering.STRING_TO_DAY]

    @classmethod
    def offeringsFromDateString(cls, dateStr):
        if dateStr.upper() == "TBA":
            return []

        match = CourseOffering.dateRE.match( dateStr )
        if not match:
            return []

        startHour, startMinute, endHour, endMinute = map(int,match.groups()[:-1])
        days = match.groups()[-1]
        # Try to guess if it is AM or PM -- waterloo does not specify
        if startHour < 8 or (startHour == 8 and startMinute < 20):
            startHour += 12
            endHour += 12
        elif endHour < 9:
            endHour += 12

        startTimeSeconds = 60*60*startHour + 60*startMinute
        endTimeSeconds = 60*60*endHour + 60*endMinute

        #Parse the differences between "T" and "Th"
        curDay = days[0]
        validDays = []
        for char in days[1:]:
            if curDay and char.isupper():
                validDays.append( curDay )
                curDay = char
            else:
                curDay += char

        validDays.append(curDay)

        return [WeeklyOffering(
            WeeklyOffering.STRING_TO_DAY[day], 
            startTimeSeconds, endTimeSeconds) for day in validDays if day in WeeklyOffering.STRING_TO_DAY]

    def conflictsWith(self, other):
        return False


class WeeklyOffering(CourseOffering):
    MONDAY    = 1
    TUESDAY   = 2
    WEDNESDAY = 3
    THURSDAY  = 4
    FRIDAY    = 5
    SATURDAY  = 6
    SUNDAY    = 7
    STRING_TO_DAY = {
        "M":  MONDAY,
        "T":  TUESDAY, 
        "W":  WEDNESDAY,
        "Th": THURSDAY,
        "F":  FRIDAY, 
        "S":  SATURDAY,
        "Su": SUNDAY
    }

    DAY_TO_STRING = dict((v,k) for k, v in STRING_TO_DAY.iteritems())


    def __init__(self, day, startTimeSeconds, endTimeSeconds):
        self.day       = day
        self.startTime = startTimeSeconds
        self.endTime   = endTimeSeconds

    def displayString(cls, offerList):
        displays = []
        weeklyKey = lambda e: "%s-%s" % (e.startTime, e.endTime)
        offerSort = sorted(offerList, key=weeklyKey)
        for k,g in itertools.groupby(offerSort, weeklyKey):
            groups = list(g)
            startTime = secondsToTime(groups[0].startTime)
            endTime   = secondsToTime(groups[0].endTime)
            displays.append("%s-%s %s" % (startTime, endTime, "".join(\
                    WeeklyOffering.DAY_TO_STRING[e.day] for e in groups)))

        return ", ".join(displays)

    #This will need to be a multimethod if I add more types of offerings
    def conflictsWith(self, other):
        return self.day == other.day \
               and self.startTime <= other.endTime \
               and self.endTime >= other.startTime
