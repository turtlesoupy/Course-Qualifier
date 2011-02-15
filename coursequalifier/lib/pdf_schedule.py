import logging
import cStringIO
from xml.sax import saxutils
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, Paragraph, BaseDocTemplate, SimpleDocTemplate, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter

def timeOfDay( time ):
    return "%d:%02d" % (  time / (60*60) , time % (60*60) / 60 )

class PDFSchedule(object):
    PAGE_WIDTH, PAGE_HEIGHT = letter

    def __init__(self, requestDict):
        self.requestDict = requestDict
        self.styles      = getSampleStyleSheet()
        self.colorIndex  = 0
        self.classColors = [0xDEDEFF, 0xFFEEDE, 0xDEFFFE, 0xFFDEF0, 0xE0FFDE,
                  0xECDEFF, 0xFFFCDE, 0xDEF1FF, 0xFFDEE1, 0xDEFFEC, 0xFCDEFF,
                  0xF1FFDE, 0xFABEDC, 0xFABECD, 0xFABEBE, 0xFACDBE, 0xFADCBE]

    def getClassColor(self):
        if self.colorIndex >= len(self.classColors):
            return colors.white

        self.colorIndex +=1
        return self.classColors[self.colorIndex -1]

    def createTable(self):
        validDays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        data = []
        headers = [["Time"] + validDays]
        stepSize = 30*60

        style = []

        responseData = self.requestDict["response_data"]
        sections = self.requestDict["sections"]

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
            dayTime = timeOfDay(time)
            data.append(  [dayTime] +  [""]*len(validDays) )


        #Bucket in our courses
        for course, section in sections.iteritems():
            sectionInfo = responseData["courses"][course]["sections"][section]
            color = self.getClassColor()
            for offering in sectionInfo["offerings"]:
                start = offering["start_time"]
                end   = offering["end_time"]

                row = (start - realStart) / stepSize
                rowEnd = (end - realStart) / stepSize
                col = offering["day"] + 1
                data[row][col] = Paragraph("<para leading='9' align='center' fontsize='7.5'>%s<br/>%s</para>" % (course, sectionInfo["building_room"] ), self.styles["BodyText"] )
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

    def sectionInformation(self, sectionInfo):
        info = [
            ("Section Number", "section_num"),
            ("Catalog Number", "class_number"),
            ("Time (s)", "date_string"),
            ("Room", "building_room"),
            ("Instructor", "instructor"),
            ("Enrollment", "enrollment")
        ]
        lines = []
        for name,key in info:
            if key in sectionInfo and sectionInfo[key]:
                lines.append("%s: %s" % (name, sectionInfo[key]))
            else:
                lines.append("%s: N/A" % name)

        return lines

    def createCatalogInformation(self):
        split = 4
        tables = []

        responseData = self.requestDict["response_data"]
        sections = self.requestDict["sections"]

        newData = []
        style = []
        style.append( ("ALIGN", (0,0), (-1,-1), "CENTER" ) )
        style.append( ("VALIGN", (0,0), (-1,-1), "TOP" ) )
        colWidth = 4.5*cm
        i = 0
        for course, section in sections.iteritems():
            courseInfo = responseData["courses"][course]
            sectionInfo = responseData["courses"][course]["sections"][section]
            lines = self.sectionInformation(sectionInfo)
            newParagraph = Paragraph("""
    <para leading="10">
    <font size="10" face="times-bold">%s</font> <br />
    <font size="6" face="times-italic">%s</font> <br />
    <font size="7.5">%s</font>
    </para>
    """ % (course, saxutils.escape(courseInfo["title"]), "<br />".join( lines )), self.styles["BodyText"] )

            newData.append( newParagraph )
            i += 1
            if i >= split:
                tables.append( Table( [newData], style=style, colWidths=[colWidth]*len(newData)  ) )
                newData = []
                i = 0

        if len( newData ) > 0 :
            tables.append( Table( [newData], style=style, colWidths = [colWidth]*len(newData)) )
        
        return tables

    def drawFooter(self, canvas, document ):
        canvas.saveState()
        canvas.setFont('Courier', 7 )
        canvas.drawString(self.PAGE_WIDTH - 7*cm, 1.5*cm, "Created by the Course Qualifier" )
        canvas.drawString(self.PAGE_WIDTH - 6.90*cm, 1.2*cm, "http://www.coursequalifier.com" )
        canvas.restoreState()

    def render(self):
        output = cStringIO.StringIO()
        doc = SimpleDocTemplate(output, pagesize = letter, topMargin=cm)
        elements = []
        #elements.append(Paragraph(logResults, self.styles["Title"]))
        elements.append(Paragraph( "<font size='22'>Schedule of Classes</font>", self.styles["Title"]))
        elements.append(self.createTable())
        elements.append(Spacer(1, 0.5*cm ))
        elements.extend(self.createCatalogInformation())
        doc.build(elements, onFirstPage=self.drawFooter)
        return output.getvalue()
