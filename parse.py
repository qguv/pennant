#!/usr/bin/env python3
# vim:si:et:ts=4:sw=4

def parseHtml(htmlText: str) -> list(tuple()):
    '''
    Input is html scraped from <courselist.wm.edu>.
    Output is a list of courses in tuple form.

    Tuples have the following format:
    0: CRN (Banner's "course registration number")
    1: department, level, and section
    2: attributes
    3: title
    4: professor
    5: credit-hours
    6: meeting days (of week)
    7: meeting times
    8: projected enrollment
    9: current enrollment
    10: seats free
    11: "OPEN" or "CLOSED"
    '''

    import re

    crnPattern = r'<td.*>\s*<a[^>]*>([^<]+)</a>\s*</td>\s*'
    dataPattern = r'<td[^>]*>([^<]+)</td>\s*'
    fullPattern = re.compile(crnPattern + dataPattern * 11)
    return re.findall(fullPattern, htmlText)

def parseToCourseList(results: list(tuple())) -> list("course.Course()"):
    '''
    Input is a list of tuples described in parseHtml().
    Output is a list of Course instances.
    '''

    import time
    from course import Course

    openMap = {
        "OPEN": True,
        "CLOSED": False
    }

    weekdayMap = {
        'M': "Monday",
        'T': "Tuesday",
        'W': "Wednesday",
        'R': "Thursday",
        'F': "Friday",
    }

    masterCourses = []

    for result in results:
        topn = openMap[result[11]]
        tcrn = result[0]

        titleData = result[1].split(" ")
        tdepart = titleData[0]
        tlevel = titleData[1]
        tsection = titleData[2]

        ttitle = result[3]
        ttitle = ttitle.replace("&amp;", '&')
        ttitle = ttitle.replace("&#39;", '\'')

        tprof = result[4]
        tcredit = result[5]

        tattrs = set()
        tgers = set()
        if result[2] != '':
            attribs = result[2].split(", ")
            for attrib in attribs:
                if "GE" in attrib:
                    tgers.add(attrib[2:])
                elif "&nbsp;" in attrib:
                    continue
                elif attrib in ('.'):
                    continue
                else:
                    tattrs.add(attrib)

        days = result[6]
        tdays = list()
        if days != '':
            for d in days:
                if d in "MTWRF":
                    tdays.append(weekdayMap[d])

        if result[7] != '' and '-' in result[7]:
            ttime = result[7]
        else:
            ttime = tuple()

        tprojectede = int(result[8])
        tcurrente = int(result[9])
        tseats = int(result[10])

        someCourse = Course(
            isOpen=topn,
            crn=tcrn,
            department=tdepart,
            level=tlevel,
            section=tsection,
            title=ttitle,
            professor=tprof,
            creditHours=tcredit,
            attributes=tattrs,
            gers=tgers,
            days=tdays,
            times=ttime,
            projectedE=tprojectede,
            currentE=tcurrente,
            seats=tseats)

        masterCourses.append(someCourse)

    return masterCourses

if __name__ == "__main__":
    with open("results.html", 'r') as f:
        rawHtml = f.read()

    parsedHtml = parseHtml(rawHtml)
    courseList = parseToCourseList(parsedHtml)

    for courseEntry in courseList:
        print(courseEntry.fullinfo())
