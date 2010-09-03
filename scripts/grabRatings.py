import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules" )))

from BeautifulSoup import BeautifulSoup
import urllib
from optparse import OptionParser
from pysqlite2 import dbapi2 as sqlite


baseURL = "http://www.ratemyprofessors.com/"
database = "rate_my_professors.db"

class Professor( object ):
    def __init__( self, firstName, lastName, quality, numberRatings, ease, url ):
        self.firstName = firstName
        self.lastName = lastName
        self.quality = quality
        self.ease = ease
        self.numberRatings = numberRatings
        self.url = url

    def __str__( self ):
        return "[%s %s : quality %f ease %f number %d url %s]" % (self.firstName, self.lastName, self.quality, self.ease, self.numberRatings, self.url)

    def addToDb(self, cursor, table ):
        cursor.execute( 'INSERT INTO %s VALUES (null, ?, ?, ?, ?, ?, ?)' % \
            table, (self.firstName, self.lastName, self.quality, self.ease, self.numberRatings, self.url ) )

    def deleteFromDb( self, cursor, table ):
        cursor.execute( 'DELETE FROM %s WHERE first_name=? AND last_name=?' % table, (self.firstName, self.lastName ) )

def getDescendantText( tag ):
    return " ".join([e.strip() for e in tag.findAll( text = lambda(text ) : len(text) > 0 ) ])

def getProfessors( soup ):
    rmp_table = soup.find( id="rmp_table" )
    headers = rmp_table.find( attrs={"class": "table_headers"} ).findAll( 'th' ) 

    headerNames = []
    for header in headers:
        headerNames.append(" ".join([e.strip() for e in header.findAll( text = lambda( text ) : len(text ) > 0 )]))

    headerMap = dict( [(e,i) for i,e in enumerate( headerNames)] )

    professors = []
    
    for row in rmp_table.findAll( "tr" ):
        cols = row.findAll("td" )
        try:
            fullName= getDescendantText(cols[headerMap["Professor's Name"]])
            url = "%s%s" % (baseURL, cols[headerMap["Professor's Name"]].find('a')["href"])
            quality = float(getDescendantText( cols[headerMap["Overall Quality"]] ))
            numberRatings = int(getDescendantText( cols[headerMap["Total Ratings"] ] ))
            ease = float(getDescendantText( cols[headerMap["Ease"] ] ))
            lastName, firstName = [e.strip() for e in fullName.split(",") ]

        except (IndexError, ValueError):
            continue

        professor = Professor( firstName, lastName, quality, numberRatings, ease, url ) 
        try:
            print professor
        except UnicodeError:
            print "(unicode)"

        professors.append( professor )

    return professors


def getAllProfessors(startUrl):
    opener = urllib.FancyURLopener()
    url = startUrl 
    professors = []
    while( 1 ):
        site = opener.open( url )
        contents = site.read()

        site.close()

        soup = BeautifulSoup( contents, convertEntities="html" )
        
        oldLen = len( professors )
        professors.extend(getProfessors( soup ))

        nav = soup.find( attrs={"class": "rmp_search_nav" } )
        if nav:
            newURL =  nav.find( text="Next").parent["href"]
            if not newURL:
                break

            try:
                newURL.index("letter=Z")
                url.index("letter=Z")
                break
            except ValueError:
                pass

            url = "%s%s" % ( baseURL,  newURL )
        else:
            break

    return professors

        
def createDB( fileName, database  ):
    con = sqlite.connect( database )
    cursor = con.cursor()
    try:
        f = open( fileName, 'r' )
        for name, url in [ e.split(",") for e in f if not e.isspace()] :
            print "Creating table", name
            cursor.execute('CREATE TABLE %s (id INTEGER PRIMARY KEY,\
            first_name VARCHAR(50), last_name VARCHAR(50), quality REAL, ease REAL, number INTEGER, url VARCHAR(512) )' % name)
        con.commit()
    finally:
        f.close()

def printDB( tableName, database ):
    con = sqlite.connect( database )
    cursor = con.cursor()
    cursor.execute('SELECT * FROM %s' % tableName )
    print cursor.fetchall()

def gatherData( fileName, database ):
    con = sqlite.connect( database )
    try:
        f = open( fileName, 'r' )
        for name, url in [ e.split(",") for e in f if not e.isspace()] :
            professors = getAllProfessors( url )
            for professor in professors:
                cursor = con.cursor()
                professor.deleteFromDb(cursor, name )
                professor.addToDb(cursor, name )
                con.commit()

    finally:
        f.close()
    
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option( "-c", "--create", dest="create", action="store_true", default=False,
                        help="Create the databases as specified by file" )
    parser.add_option( "-f", "--file", dest="filename",
                        help="file for all databases" )

    parser.add_option( "-p", "--print", dest="print_db",
                        help="print the contents of a specific table" )

    parser.add_option( "-d", "--database", dest="database",
                        help="database to write to" )

    (options, args) = parser.parse_args()

    if not options.database:
        print "Please specify the -d option"
        sys.exit(2)

    if options.create:
        createDB( options.filename, options.database )
    elif options.print_db:
        printDB( options.print_db, options.database )
    else:
        gatherData( options.filename, options.database )
