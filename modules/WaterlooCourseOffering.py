import os
import re
import sys
import simplejson

# This class can be expanded to include biweekly offerings
class WaterlooCourseOffering(object):
    dateRE = re.compile( "(\d{2}):(\d{2})-(\d{2}):(\d{2})(\w+)" )

    @classmethod
    def offeringsFromDateString(cls, dateStr):
        if dateStr.upper() == "TBA":
            return []

        match = WaterlooCourseOffering.dateRE.match( dateStr )
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

        return [WaterlooWeeklyOffering(
            WaterlooWeeklyOffering.STRING_TO_DAY[day], 
            startTimeSeconds, endTimeSeconds) for day in validDays]

    def getJson(self):
        return {
            "type": "courseOffering"
        }

    def conflictsWith(self, other):
        return False


class WaterlooWeeklyOffering(WaterlooCourseOffering):
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

    def __init__(self, day, startTimeSeconds, endTimeSeconds):
        self.day       = day
        self.startTime = startTimeSeconds
        self.endTime   = endTimeSeconds

    #This will need to be a multimethod if I add more types of offerings
    def conflictsWith(self, other):
        return self.day == other.day \
               and self.startTime <= other.endTime \
               and self.endTime >= other.startTime

    def getJson(self):
        return {
            "type":       "weeklyOffering",
            "day":        self.day,
            "start_time": self.startTime,
            "end_time":   self.endTime
        }

    def jsonDump(self):
        return simplejson.dumps(self.getJson())
