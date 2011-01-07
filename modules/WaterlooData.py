import json
import logging
import QualifierExceptions
from httplib import HTTPConnection
from urllib import urlencode, quote

import QualifierConfig
from QualifierConfig import config

def pullCourseInfo(acronym, number):
    try:
        return getJSONFromPath("/v1/course/%s/%s.json" % (quote(acronym), quote(number)))
    except QualifierExceptions.CourseMissingException, e:
        #Raise a nicer error string
        raise QualifierExceptions.CourseMissingException("Missing course %s %s" % (acronym, number))

def pullSectionInfo(acronym, number, term):
    return getJSONFromPath("/v1/course/%s/%s/schedule.json" % (quote(acronym), 
        quote(number)), [("term",quote(term))])

def pullSearchCourses(query):
    return getJSONFromPath(
        "/v1/course/search.json", [("q", query)]
    )

def getJSONFromPath(basePath, query=[]):
    connection = HTTPConnection(config.uwdataAddress)

    path = "%s?key=%s%s" %  \
            (basePath, config.uwdataKey, "".join("&%s=%s" % (k,v) for k,v in query))

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
                raise QualifierExceptions.CourseMissingException()
            else:
                raise QualifierExceptions.DataError(data['error']['text'])
        else:
            raise QualifierExceptions.DataError(data['error'])

    return data

def main():
    pass

if __name__ == "__main__":
    main()
