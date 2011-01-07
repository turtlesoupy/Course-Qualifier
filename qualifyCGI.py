#!/usr/bin/python -u
import os
import cgi
import sys
import logging
import cStringIO
import traceback

sys.path.append( os.path.join( sys.path[0], "modules" ) )

import simplejson
import QualifierConfig
import QualifierExceptions

def main():
    print "Content-Type: text/json"
    print

    QualifierConfig.readDefault()
    jsonLogStream = cStringIO.StringIO()
    console = logging.StreamHandler( jsonLogStream )
    formatter = logging.Formatter( "%(levelname)s: %(message)s" )
    console.setFormatter( formatter )
    console.setLevel( logging.DEBUG )
    logging.getLogger('').addHandler( console )
    logging.getLogger('').setLevel( logging.DEBUG )

    form = cgi.FieldStorage()
    jsonOutput = cStringIO.StringIO()
    jsonInput = simplejson.loads(form.getfirst("json"))

    school = jsonInput["school"]
    if school.lower() == "waterloo":
        from WaterlooDispatcher import WaterlooDispatcher as Dispatcher
    else:
        raise RuntimeError( "Unsupported school specified!" )

    
    try:
        blah = Dispatcher( jsonInput)
        simplejson.dump( {"result": blah.dispatch(), "info": jsonLogStream.getvalue() }, jsonOutput )
    except QualifierExceptions.QualifierException, e:
        simplejson.dump( {"exception": e.getJson() }, jsonOutput )

    print '%s' % jsonOutput.getvalue()

if __name__ == "__main__":
    try:
        main()
    except:
        tracebackIO = cStringIO.StringIO()
        traceback.print_exc( file=tracebackIO )
        
        jsonIO = cStringIO.StringIO()
        simplejson.dump ( {"error": tracebackIO.getvalue() }, jsonIO )

        print jsonIO.getvalue()
