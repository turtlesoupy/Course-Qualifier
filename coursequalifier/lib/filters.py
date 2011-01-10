#Section Filters
class SectionFilter(object):
    def passes(self, section):
        return False

class NotFullFilter(SectionFilter):
    def passes(self, section):
        return not section.full()

class StartsAfterFilter(SectionFilter):
    def __init__(self, afterTime):
        self.afterTime = afterTime

    def passes(self, section):
        return section.startsAfter(self.afterTime)

class EndsBeforeFilter(SectionFilter):
    def __init__(self, beforeTime):
        self.beforeTime = beforeTime

    def passes(self, section):
        return section.endsBefore(self.beforeTime)

#Course Filters
class CourseFilter(object):
    def passes(self, course):
        return False

class CourseTypesFilter(CourseFilter):
    def __init__(self, goodTypes, hasOther, otherProhibition=[]):
        self.goodTypes        = goodTypes
        self.hasOther         = hasOther
        self.otherProhibition = otherProhibition

    def passes(self, course):
        if course.type in self.goodTypes:
            return True
        elif self.hasOther and course.type not in self.otherProhibition:
            return True
        else:
            return False


#Course Group Filters
class CourseGroupFilter(object):
    def passes(self, courseGroup):
        pass

#Catalog Filters
class CatalogFilter(object):
    def passes(self, catalog):
        return False

class RequiredSectionsFilter(CatalogFilter):
    def __init__(self, courseGroup, requiredSectionNumbers=set()):
        self.courseGroup = courseGroup
        self.courseNames = [e.uniqueName for e in courseGroup]
        self.requiredSectionNumbers = requiredSectionNumbers

    def passes(self, catalog):
        scopedNums = set(e.sectionNum for e in catalog.sections if e.courseName in self.courseNames)
        print scopedNums
        print self.requiredSectionNumbers
        return len(self.requiredSectionNumbers - scopedNums) == 0

