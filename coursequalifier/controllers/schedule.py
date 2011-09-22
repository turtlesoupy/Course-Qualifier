import re
import json
import base64
import logging
from itertools import chain

from pylons import request, response, session, tmpl_context as c, config
from pylons.controllers.util import abort

from coursequalifier.lib.uwdata import CourseMissingException, UWDataError
from coursequalifier.lib.base import BaseController, render
from coursequalifier.lib.pdf_schedule import PDFSchedule
from coursequalifier.lib.filters import NotFullFilter, \
        CourseTypesFilter, RequiredSectionsFilter, StartsAfterFilter, EndsBeforeFilter
from coursequalifier.model.course import Course
from coursequalifier.model.catalog import Catalog
from coursequalifier.model.course_section import CourseSection
from coursequalifier.model.course_offering import WeeklyOffering

log = logging.getLogger(__name__)

class ScheduleController(BaseController):
    directRE = re.compile(r"\s*([A-Za-z]+)\s*(\d\d\d\w*)")
    def compute_all(self):
        response.content_type = "application/json"

        r = json.loads(request.params['json'])
        term = r['term']
        requestSectionFilters = self._request_section_filters(r)
        catalogFilters = []
        searchGroups  = []
        directCourses = []
        for course in r['courses']:
            query = course["course_query"].strip()
            if query == "": continue

            courseFilters = self._course_filters(course["options"])
            m = self.directRE.match(query)
            if m:
                try:
                    courses = Course.coursesFromCode(m.group(1), m.group(2), term,\
                            sectionFilters=requestSectionFilters)
                except CourseMissingException, e:
                    return json.dumps({"error": {
                        "type":  "no_query_results",
                        "query": query
                    }})
                except UWDataError, e:
                    return json.dumps({"error": {
                        "type":  "uwdata",
                        "query": query
                    }})

                catalogFilters.extend(self._course_catalog_filters(courses, course["options"]))
                directCourses.extend([e for e in courses\
                    if all(courseFilter.passes(e) for courseFilter in courseFilters)])
            else:
                courseGroups = []
                try:
                    for courseGroup in Course.courseGroupsFromSearch(query, term, sectionFilters=requestSectionFilters):
                        filteredGroup = [e for e in courseGroup if all(courseFilter.passes(e) for courseFilter in courseFilters)]
                        if len(filteredGroup) > 0:
                            courseGroups.append(filteredGroup)
                except CourseMissingException, e:
                    return json.dumps({"error": {
                        "type":  "no_query_results",
                        "query": query
                    }})
                except UWDataError, e:
                    return json.dumps({"error": {
                        "type": "uwdata",
                        "query": query
                    }})

                catalogFilters.extend(self._course_catalog_filters(chain(*courseGroups), course["options"]))
                searchGroups.append(courseGroups)

        allCourses       = directCourses + list(chain(*([chain(*e) for e in searchGroups])))
        searchSpaceCount = Catalog.searchSpaceCount(directCourses, searchGroups)
        if searchSpaceCount > int(config['maxSearchSpace']):
            return json.dumps({"error": {
                "type": "large_search_space",
                "size": searchSpaceCount
            }})

        catalogs, conflicts = Catalog.computeAll(directCourses, searchGroups)

        filteredCatalogs= [c for c in catalogs \
                if all(catalogFilter.passes(c) for catalogFilter in catalogFilters)]

        return json.dumps({"result": {
            "courses":     dict((e.uniqueName, self._course_dict(e)) for e in allCourses),
            "conflicts":   [self._conflict_dict(c) for c in conflicts],
            "catalogs":    [self._catalog_dict(c) for c in filteredCatalogs]
        }})

    def pdf(self):
        r = json.loads(base64.b64decode(request.params['ugly_url']))
        pdf = PDFSchedule(r)
        response.content_type = "application/pdf"
        return pdf.render()

    def _course_filters(self, courseOptions):
        ret = []

        validTypes = set(["LEC"])
        hasOther = False
        if "tests" in courseOptions and courseOptions["tests"] == True:
            validTypes.add("TST")
        if "tutorials" in courseOptions and courseOptions["tutorials"] == True:
            validTypes.add("TUT")
        if "other" in courseOptions and courseOptions["other"] == True:
            hasOther = True

        ret.append(CourseTypesFilter(validTypes, hasOther, set(["LEC", "TST", "TUT"])))

        return ret

    def _course_catalog_filters(self, courses, courseOptions):
        ret = []
        sectionNums = set(e.strip() for e in courseOptions["sections"] if e.strip() != "")
        if len(sectionNums) > 0:
            ret.append(RequiredSectionsFilter(courses, sectionNums))

        return ret

    def _request_section_filters(self, req):
        ret = []
        options = req['options']
        if not options['show_full_courses'] or options['show_full_courses'] == False:
            ret.append(NotFullFilter())

        endsEarlierThanHour   = options["ends_earlier_than_hour"].strip()
        endsEarlierThanMinute = options["ends_earlier_than_minute"].strip()
        endsEarlierThanAMPM   = options["ends_earlier_than_ampm"].strip()
        if endsEarlierThanHour != "" and endsEarlierThanMinute != "" and endsEarlierThanAMPM != "":
            earlyTime = 60*60*int(endsEarlierThanHour) + 60*int(endsEarlierThanMinute)
            if endsEarlierThanHour == "12":
                earlyTime -= 12*60*60
            if endsEarlierThanAMPM == "PM":
                earlyTime += 12*60*60
            ret.append(EndsBeforeFilter(earlyTime))

        startsLaterThanHour   = options["starts_later_than_hour"].strip()
        startsLaterThanMinute = options["starts_later_than_minute"].strip()
        startsLaterThanAMPM   = options["starts_later_than_ampm"].strip()
        if startsLaterThanHour != "" and startsLaterThanMinute != "" and startsLaterThanAMPM != "":
            lateTime = 60*60*int(startsLaterThanHour) + 60*int(startsLaterThanMinute)
            if startsLaterThanHour == "12":
                lateTime -= 12*60*60
            if startsLaterThanAMPM == "PM":
                lateTime += 12*60*60
            ret.append(StartsAfterFilter(lateTime))

        return ret

    def _conflict_dict(self, conflict):
        s1,s2 = conflict
        return [{ "courseName": s.courseName,
                  "sectionNum": s.sectionNum
                } for s in (s1,s2)]

    
    def _course_dict(self, course):
        return {
            "courseName":  course.uniqueName,
            "type":        course.type,
            "description": course.description,
            "title":       course.title,
            "sections":    dict((e.classNumber, self._section_dict(e))
                                for e in course.sections)
        }

    def _section_dict(self, section):
        return {
            "class_number":  section.classNumber,
            "section_num":   section.sectionNum,
            "instructor":    section.instructor,
            "building_room": section.buildingRoom,
            "campus":        section.campus,
            "offerings":     [self._offering_dict(o) for o in section.offerings],
            "related1":      section.related1,
            "related2":      section.related2,
            "date_string":   section.dateString,
            "enrollment":    "%s / %s" % (section.enrlTot, section.enrlCap)
        }

    def _offering_dict(self, offering):
        if isinstance(offering, WeeklyOffering):
            return {
                "type":       "weeklyOffering",
                "day":        offering.day,
                "start_time": offering.startTime,
                "end_time":   offering.endTime
            }
        else:
            return {"type": "unknownOffering"}

    def _catalog_dict(self, catalog):
        return {
            "metrics": catalog.metrics,
            "sections": [{
                "courseName":  section.courseName,
                "sectionName": section.classNumber
            } for section in catalog.sections]
        }
