#! /usr/bin/env python
import sys
import os
from optparse import OptionParser
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules" )))

import Databases
from pysqlite2 import dbapi2 as sqlite


def createTables( school, database ):
    con = sqlite.connect( database )
    cursor = con.cursor()
    print ""
    print "%s:" % school
    try:
        print "Creating table qualify_requests" 
        cursor.execute( "CREATE TABLE qualify_requests (id INTEGER PRIMARY KEY, \
        time DATETIME, ip VARCHAR( 64), term VARCHAR( 10 ))" )
    except sqlite.OperationalError, e:
        print '\t', e
    
    print "Creating table qualify_request_courses"
    try:
        cursor.execute( "CREATE TABLE qualify_request_courses (id INTEGER PRIMARY KEY, \
        request_id INTEGER, subject VARCHAR( 64 ), code VARCHAR( 64 ), \
        FOREIGN KEY( request_id ) REFERENCES qualify_requests(id))" )
    except sqlite.OperationalError, e:
        print '\t', e

    print "Creating table qualify_request_conflicts"
    try:
        cursor.execute( "CREATE TABLE qualify_request_conflicts (id INTEGER PRIMARY KEY, \
        request_id INTEGER, course1 VARCHAR( 64 ), course2 VARCHAR( 64 ), \
        FOREIGN KEY( request_id ) REFERENCES qualify_requests(id))" )
    except sqlite.OperationalError, e:
        print '\t', e

def main():
    for name, database in Databases.statisticsDbs:
        createTables( name, database )

if __name__ == "__main__":
    main()
