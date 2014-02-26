#!/usr/bin/env python3
# vim:si:et:ts=4:sw=4

import time
import json


class Course:

    def __init__(self, **kwargs):
        self.isOpen = bool(kwargs["isOpen"])
        self.crn = int(kwargs["crn"])
        self.department = str(kwargs["department"])
        self.level = str(kwargs["level"])
        self.section = str(kwargs["section"])
        self.title = str(kwargs["title"])
        self.professor = str(kwargs["professor"])
        self.creditHours = str(kwargs["creditHours"])
        self.attributes = set(kwargs["attributes"])
        self.gers = set(kwargs["gers"])
        self.days = list(kwargs["days"])
        self.projectedE = int(kwargs["projectedE"])
        self.currentE = int(kwargs["currentE"])
        self.seats = int(kwargs["seats"])

        self.professorLast = self.professor.split(",")[0]

        if kwargs["times"] != '' and '-' in kwargs["times"]:
            self.times = kwargs["times"]
            self.times = self.times.split('-')
            starttime = time.strptime(self.times[0], "%H%M")
            endtime = time.strptime(self.times[1], "%H%M")
            self.times = (starttime, endtime)
        else:
            self.times = tuple()

    def oneline(self):
        pattern = "{}: {} w/ Prof. {} ({} {}-{}, CRN {})"
        return pattern.format(
            "OPEN" if self.isOpen else "CLOSED",
            self.title,
            self.professorLast,
            self.department,
            self.level,
            self.section,
            self.crn,
        )

    def __str__(self):
        pattern = "{} w/ Prof. {}\n"
        pattern += "    {} ({} {}-{}, CRN {})\n"
        return pattern.format(
            self.title,
            self.professorLast,
            "OPEN" if self.isOpen else "CLOSED",
            self.department,
            self.level,
            self.section,
            self.crn,
        )

    def fullinfo(self):
        try:
            humanTime = time.strftime("%I:%M %p", self.times[0]) \
                + " to " + time.strftime("%I:%M %p", self.times[1])
        except IndexError:
            humanTime = ''

        pattern = "{} w/ Prof. {}\n    "
        pattern += "{} ({} {}-{}, CRN {})\n    "
        pattern += "{}{}{}"
        pattern += "fulfills {}\n    "
        pattern += "{} credit{}{}{}\n"
        return pattern.format(
            self.title,
            self.professorLast,
        # newline
            "OPEN" if self.isOpen else "CLOSED",
            self.department,
            self.level,
            self.section,
            self.crn,
        # newline
            ", ".join(self.days) if self.days else '',
            " from " if self.days and humanTime else \
                "meets from " if humanTime else '',
            humanTime + "\n    " if self.days or humanTime else '',
        # newline
            "GER " + ", ".join(sorted(self.gers)) if self.gers else "no GERs",
        # newline
            self.creditHours,
            's' if self.creditHours != '1' else '',
            ": " if self.attributes else '',
            ", ".join(sorted(self.attributes)) if self.attributes else '',
        )

    def toJSON(self):
        timeTuple = self.times
        if len(timeTuple) == 2:
            timeTuple = (time.strftime("%H%M",self.times[0]),time.strftime("%H%M",self.times[1]))
        else:
            timeTuple = ("","")
        jsonStr = json.dumps({"level":self.level,"isOpen":self.isOpen,"crn":self.crn,"title":self.title,"department":self.department,"section":self.section,"professor":self.professor,"creditHours":self.creditHours,"attributes":list(self.attributes),"gers":list(self.gers),"days":list(self.days),"times":list(timeTuple),"projectedE":self.projectedE,"currentE":self.currentE,"seats":self.seats})
        return jsonStr


def TestCourse():
    dataStructures = Course(
        isOpen=True,
        crn=12345,
        department="CSCI",
        level="241",
        section=1,
        title="Data Structures",
        professor="Dickerson, Robert F.",
        creditHours="3",
        attributes={},
        gers={},
        days={"Monday", "Wendsday"},
        times="1400-1520",
        projectedE=40,
        currentE=39,
        seats=1,
    )
    print("Data Structures Course, standard output:\n\n", dataStructures, "\n\n")
    print("Data Structures Course, oneline:\n\n", dataStructures.oneline(), "\n\n")
    print("Data Structures Course, fullinfo:\n\n", dataStructures.fullinfo())

def scrapeCourselist() -> str:
    '''Outputs raw html scraped from <courselist.wm.edu>.'''

    import requests

    url = "https://courselist.wm.edu/courseinfo/searchresults"
    payload = {
        "term_code": "201420",  # Spring 2014
        "term_subj": "0",       # ALL
        "attr": "0",            # ALL
        "levl": "0",            # ALL
        "status": "0",          # ALL
    }
    r = requests.post(url, payload)
    response = r.text
    response = response.replace("\r", "\n")
    return response

def writeCourselist(filename: str):
    '''Writes raw html scraped from <courselist.wm.edu> to given file.'''

    response = scrapeCourselist()
    with open(filename, 'w') as f:
        f.write(response)

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

def parseToCourseList(results: list(tuple())) -> list():
    '''
    Input is a list of tuples described in parseHtml().
    Output is a list of Course instances.
    '''

    import time

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

def TestParse():
    with open("results.html", 'r') as f:
        rawHtml = f.read()

    parsedHtml = parseHtml(rawHtml)
    courseList = parseToCourseList(parsedHtml)

    for courseEntry in courseList:
        print(courseEntry.fullinfo())

def autoCourseList() -> list():
    with open("results.html", 'r') as f:
        rawHtml = f.read()

    parsedHtml = parseHtml(rawHtml)
    courseList = parseToCourseList(parsedHtml)
    
    return courseList

