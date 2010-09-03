#!/usr/bin/python2.4 -u
import os
import sys
import operator
from optparse import OptionParser
sys.path.append( os.path.join( sys.path[0], "modules" ) )

import Databases
from mako.template import Template
from mako import exceptions

from pysqlite2 import dbapi2 as sqlite

statisticsCon = sqlite.connect( Databases.waterlooStatistics )
statCon = statisticsCon.cursor()

class memoized(object):
   """Decorator that caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned, and
   not re-evaluated.
   """
   def __init__(self, func):
      self.func = func
      self.cache = {}
   def __call__(self, *args):
      try:
         return self.cache[args]
      except KeyError:
         self.cache[args] = value = self.func(*args)
         return value
      except TypeError:
         # uncachable -- for instance, passing a list as an argument.
         # Better to not cache than to blow up entirely.
         return self.func(*args)
   def __repr__(self):
      """Return the function's docstring."""
      return self.func.__doc__

def contentType():
    return "Content-Type: text/html\r\n"

def embedGooglePieChart( data, labels, style='' ):
    return """
<img src="http://chart.apis.google.com/chart?\
chs=500x250\
&amp;chd=t:%s\
&amp;cht=p\
&amp;chl=%s"
alt="" style="%s"/>
""" % ( data, labels,  style )

def googleChartData( dataList ):
   total = sum(dataList) 
   return ",".join( "%.1f" % (float(e) / total * 100) for e in dataList)

@memoized
def numRequests():
    statCon.execute( "SELECT count(1) FROM qualify_requests" )
    return statCon.fetchall()[0][0]

@memoized
def numDistinctRequests():
    statCon.execute( "SELECT COUNT( DISTINCT ip ) FROM qualify_requests" )
    return statCon.fetchall()[0][0]

@memoized
def numRequestCourses():
    statCon.execute( "SELECT count(1) FROM qualify_request_courses" )
    return statCon.fetchall()[0][0]
    

@memoized
def subjectNumbers(limit=10):
    statCon.execute( "SELECT subject, count(1) as num FROM qualify_request_courses \
GROUP BY subject ORDER BY num DESC LIMIT %d" % limit )
    results = statCon.fetchall()
    total = sum( int(b) for a,b in results )
    otherNum = numRequestCourses() - total
    if otherNum > 0:
        results.append( ("Other", otherNum ) )
    return results

    
@memoized
def subjectChart(limit=10):
    chd = googleChartData( [b for a,b in subjectNumbers()] )
    chl = "|".join( a for a,b in subjectNumbers() )
    return embedGooglePieChart( chd, chl )

@memoized
def courseNumbers(limit=10):
    statCon.execute( "SELECT subject, code, count(1) as num FROM qualify_request_courses \
GROUP BY subject, code ORDER BY num DESC LIMIT %d" % limit )
    results = statCon.fetchall() 
    total = sum( int(c) for a,b,c in results )
    otherNum = numRequestCourses() - total
    if otherNum > 0:
        results.append( ("Other", "", otherNum ) )
    return results


@memoized
def courseChart(limit=10):
    results = courseNumbers(limit) 
    chd = googleChartData([c for a,b,c in results])
    chl = "|".join( "%s %s" % (a,b) for a,b,c in results )
    return embedGooglePieChart( chd, chl )
    

@memoized
def oftenConflicting( limit=5 ):
    statCon.execute( "SELECT course1, course2, count(1) as conflicts FROM qualify_request_conflicts\
    GROUP BY course1,course2 ORDER BY conflicts DESC LIMIT %d" % limit )
    return statCon.fetchall()

    

@memoized
def popularPairs(limit=5):
    cursor = statisticsCon.cursor()
    cursor.execute( "SELECT subject, code,request_id FROM qualify_request_courses ORDER BY request_id" )

    pairHash = {}
    #This should be about as clear as Seattle
    def processRowGroup( rowGroup ):
        for row_1 in rowGroup:
            for row_2 in rowGroup:
                if row_2 == row_1:
                    continue

                subject_1, code_1, request_1 = row_1
                subject_2, code_2, request_2 = row_2

                courseName1 = "%s %s" % (subject_1, code_1 )
                courseName2 = "%s %s" % (subject_2, code_2 )
                toHash = (courseName1, courseName2)
                if courseName1 > courseName2:
                    toHash = (courseName2, courseName1 )

                if toHash in pairHash:
                    pairHash[toHash] += 1
                else:
                    pairHash[toHash] = 1


    lastRequestId = None
    groupedRows = []
    for row in cursor:
        subject, code, requestId = row
        if lastRequestId == None:
            lastRequestId = requestId
        elif requestId != lastRequestId:
            processRowGroup( groupedRows )
            groupedRows = []
            lastRequestId = requestId

        groupedRows.append( row )

    processRowGroup( groupedRows )
    
    sortedPairs = sorted( ((k,v) for k,v in pairHash.iteritems()), key=lambda x: (-x[1],x[0]))

    return sortedPairs[:limit]
    
def main():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename" )
    (options, args) = parser.parse_args()

    if options.filename:
        try:
            template = Template( filename=os.path.join( sys.path[0], 'waterlooStats.mako') ) 
            string = template.render()
            f = open( options.filename, 'w')
            try:
                print >>f, string
            finally:
                f.close()
        except:
            print >>f, exceptions.html_error_template().render()
    else:
        print contentType()
        try:
            template = Template( filename=os.path.join( sys.path[0], 'waterlooStats.mako') ) 
            print template.render()
        except:
            print exceptions.html_error_template().render()

if __name__ == "__main__":
    main()
