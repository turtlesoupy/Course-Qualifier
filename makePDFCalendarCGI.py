#!/usr/bin/python -u
import os
import sys
import cgi
import logging
import cStringIO
import base64
import traceback
from xml.sax import saxutils

sys.path.append( os.path.join( sys.path[0], "modules" ) )

import simplejson
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, Paragraph, BaseDocTemplate, SimpleDocTemplate, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter

styles = getSampleStyleSheet()

def timeOfDay( time ):
    return "%d:%02d" % (  time / (60*60) , time % (60*60) / 60 )

classColors = [0xDEDEFF, 0xFFEEDE, 0xDEFFFE, 0xFFDEF0, 0xE0FFDE, 0xECDEFF, 0xFFFCDE, 0xDEF1FF, 0xFFDEE1, 0xDEFFEC, 0xFCDEFF, 0xF1FFDE, 0xFABEDC, 0xFABECD, 0xFABEBE, 0xFACDBE, 0xFADCBE]
colorIndex = 0

PAGE_WIDTH, PAGE_HEIGHT = letter

def getClassColor():
    global colorIndex
    global classColors 
    if colorIndex >= len( classColors):
        return colors.white
    
    ret = classColors[colorIndex]
    colorIndex += 1
    return ret


    
def createTable(requestDict):
    validDays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    data = []
    headers = [["Time"] + validDays]
    stepSize = 30*60

    style = []

    responseData = requestDict["response_data"]
    sections = requestDict["sections"]

    earliestStart = None
    latestEnd = None
    #First pass, determine boundaries
    for course, section in sections.iteritems():
        sectionInfo = responseData["courses"][course]["sections"][section]
        for offering in sectionInfo["offerings"]:
            startTime = offering["start_time"]
            endTime   = offering["end_time"]
            if startTime and (not earliestStart or startTime < earliestStart):
                earliestStart = startTime
            if endTime and (not latestEnd or endTime > latestEnd):
                latestEnd = endTime

    if earliestStart == None or latestEnd == None:
        realStart = 0
        realEnd = 0
    else:
        realStart = 8*60*60
        realEnd = 21*60*60
        if earliestStart <= realStart:
            realStart = earliestStart - 60*60/2
        if latestEnd >= realEnd:
            realEnd = latestEnd  + 2*60*60


    #Create blank data
    for i in xrange(( realEnd - realStart ) / stepSize + 1) :
        time = i * stepSize + realStart
        dayTime = timeOfDay(time )
        data.append(  [dayTime] +  [""]*len(validDays) )


    #Bucket in our courses
    for course, section in sections.iteritems():
        sectionInfo = responseData["courses"][course]["sections"][section]
        color = getClassColor()
        for offering in sectionInfo["offerings"]:
            start = offering["start_time"]
            end   = offering["end_time"]

            row = (start - realStart) / stepSize
            rowEnd = (end - realStart) / stepSize
            col = offering["day"] + 1
            data[row][col] = Paragraph("<para leading='9' align='center' fontsize='7.5'>%s<br/>%s</para>" % (course, sectionInfo["room"] ), styles["BodyText"] )
            style.append( ("BACKGROUND", (col, row+1), (col, rowEnd +1), color ) )
            style.append( ("SPAN", (col,row+1), (col,rowEnd+1)) )

    
    style.append( ("BACKGROUND", (0, 0), (-1, 0), colors.black ) )
    style.append( ("TEXTCOLOR", (0, 0), (-1, 0), colors.white ) )
    style.append( ("GRID", (1,1), (-1,-1 ),0.5, (0.85,0.85,0.85) ) )
    style.append( ("LINEAFTER", (0,0), (0,len(data)),0.5, colors.black ) )
    style.append( ("BOX", (0,0), (-1,-1 ),1, colors.black ) )
    style.append( ("LINEBELOW", (0,0), (-1, 0), 1, colors.black ) )
    style.append( ("VALIGN", (0,0), (-1,-1), "MIDDLE" ) )
    style.append( ("ALIGN", (0,0), (-1,-1), "CENTER" ) )

    colWidths = [1.2*cm] + [2.3*cm] * len(validDays )
    rowHeights = [0.5*cm]* (len( headers) + len(data ))
    return Table(headers + data, style=style, colWidths=colWidths, rowHeights=rowHeights)

def createCatalogInformation( requestDict ):
    split = 4
    tables = []

    responseData = requestDict["response_data"]
    sections = requestDict["sections"]

    newData = []
    style = []
    style.append( ("ALIGN", (0,0), (-1,-1), "CENTER" ) )
    style.append( ("VALIGN", (0,0), (-1,-1), "TOP" ) )
    colWidth = 4.5*cm
    i = 0
    for course, section in sections.iteritems():
        courseInfo = responseData["courses"][course]
        sectionInfo = responseData["courses"][course]["sections"][section]
        lines = [] 
        for info in responseData["section_information"]:
            if sectionInfo[info["key"]]:
                lines.append( "%s: %s" % ( info["name"], sectionInfo[info["key"]] ) )
            else:
                lines.append( "%s: N/A" % info["name"] )

        newParagraph = Paragraph("""
<para leading="10">
<font size="10" face="times-bold">%s</font> <br />
<font size="6" face="times-italic">%s</font> <br />
<font size="7.5">%s</font>
</para>
""" % (course, saxutils.escape(courseInfo["description"]), "<br />".join( lines )), styles["BodyText"] )

        newData.append( newParagraph )
        i += 1
        if i >= split:
            tables.append( Table( [newData], style=style, colWidths=[colWidth]*len(newData)  ) )
            newData = []
            i = 0

    if len( newData ) > 0 :
        tables.append( Table( [newData], style=style, colWidths = [colWidth]*len(newData)) )
    
    return tables

def drawFooter( canvas, document ):
    canvas.saveState()
    canvas.setFont('Courier', 7 )
    canvas.drawString(PAGE_WIDTH - 7*cm, 1.5*cm, "Created by the Course Qualifier" )
    canvas.drawString(PAGE_WIDTH - 7.1*cm, 1.2*cm, "http://www.coursequalifier.com" )
    canvas.restoreState()

def main():

    logStream = cStringIO.StringIO()
    console = logging.StreamHandler( logStream )
    formatter = logging.Formatter( "%(levelname)s: %(message)s" )
    console.setFormatter( formatter )
    console.setLevel( logging.DEBUG )
    logging.getLogger('').addHandler( console )
    logging.getLogger('').setLevel( logging.DEBUG )


    form = cgi.FieldStorage()
    jsonInput = simplejson.loads(base64.b64decode(form.getfirst("ugly_url")) )
    output = cStringIO.StringIO()
    doc = SimpleDocTemplate( output, pagesize = letter, topMargin=cm )
    elements = []
    logResults = logStream.getvalue()
    elements.append( Paragraph(logResults, styles["Title"]) )
    elements.append( Paragraph( "<font size='22'>Schedule of Classes</font>", styles["Title"] ) )
    elements.append( createTable(jsonInput ) )
    elements.append( Spacer(1, 0.5*cm ) )
    elements.extend( createCatalogInformation( jsonInput ) )

    logs = [] 
    for line in logStream.getvalue().split("\n"):
        logs.append(  Paragraph(line, styles["Normal"]) )
        
    logs.extend( elements )
    doc.build( logs, onFirstPage =drawFooter )

    print "Content-Type: application/pdf"
    print 
    print output.getvalue()

if __name__ == "__main__":
    try:
        main()
    except:
        print "Content-Type: text/html"
        print

        tracebackIO = cStringIO.StringIO()
        traceback.print_exc( file=tracebackIO )

        print tracebackIO.getvalue().replace("\n", "<br />") 
