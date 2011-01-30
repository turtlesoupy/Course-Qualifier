import json
import logging
from pylons import config
from httplib import HTTPConnection
from urllib import urlencode, quote

class CourseMissingException(RuntimeError): pass
class UWDataError(RuntimeError): pass

def pullCourseInfo(acronym, number):
    try:
        return getJSONFromPath("/v1/course/%s/%s.json" % (quote(acronym), quote(number)))
    except CourseMissingException, e:
        #Raise a nicer error string
        raise CourseMissingException("Missing course %s %s" % (acronym, number))

def pullSectionInfo(acronym, number, term):
    return getJSONFromPath("/v1/course/%s/%s/schedule.json" % (quote(acronym), 
        quote(number)), [("term",quote(term))])

def pullSearchCourses(query):
    return getJSONFromPath(
        "/v1/course/search.json", [("q", query)]
    )

def getJSONFromPath(basePath, query=[]):
    connection = HTTPConnection(config['uwdata.address'])

    path = "%s?key=%s%s" %  \
            (basePath, config['uwdata.key'], "".join("&%s=%s" % (k,v) for k,v in query))

    connection.request("GET", path)
    response = connection.getresponse()

    if response.status != 200:
        raise RuntimeError("Bad response from UWData")

    data = json.loads(response.read())
    response.close()
    if 'error' in data:
        if 'text' in data['error']:
            text = data['error']['text']
            if text == "Unknown course":
                raise CourseMissingException()
            elif text == "No courses found":
                raise CourseMissingException()
            else:
                raise UWDataError(data['error']['text'])
        else:
            raise UWDataError(data['error'])

    return data
