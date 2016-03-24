#!/usr/bin/env python3
# vim:si:et:ts=4:sw=4

import time
import json
import sqlite3
import requests
import re

def numeric(alphanumeric):
    return int(''.join(c for c in alphanumeric if c.isdigit()))

def is_undergrad(course):
    # labs are special
    if course.level[-1].upper() == 'L':
        level = int(course.level[:-1])

    # most courses
    try:
        level = int(course.level)

    # when in doubt, it's undergrad
    except ValueError:
        return True
    
    return level > 100 and level < 500

class Course:
    '''An object representing a W&M course. Has the following attributes:

    isOpen: whether the course is listed as taking more students,
    regardless of whether the room accomodates

    crn: Banner's course registration number

    department: the department hosting the course. For cross listed
    courses, there will be multiple course entries.

    level: the traditional-style course number, e.g. "303" for CSCI
    303. This must be a string, because some course numbers, like
    private lessons or freshman seminars, aren't numeric.

    section

    title: the Banner-abbreviated course name

    professor: the lecturer or professor instructing the course

    creditHours: how many credits the course is worth

    attributes: what COLLs or special attributes (lab fee and the like) are
    associated with the course

    gers: which General Education Requirements the course fulfills
    [deprecated, but grandfathered until 2018]

    days: which days the course meets

    projectedE: Banner's always-wrong "Projected Enrollment"

    currentE: Banner's often-wrong "Current Enrollment"

    seats: Banner's usually-wrong "Seats Remaining"

    professorLast: instructor's last name

    times: the times the course is held
    '''

    def __init__(self, **kwargs):
        self.isOpen = bool(kwargs["isOpen"])
        self.crn = int(kwargs["crn"])
        self.department = str(kwargs["department"])
        self.level = str(kwargs["level"])
        self.section = str(kwargs["section"])
        self.title = str(kwargs["title"])
        self.professor = str(kwargs["professor"])
        self.creditHours = str(kwargs["creditHours"])
        self.attributes = kwargs["attributes"]
        if self.attributes == "set()":
            self.attributes = ""
        self.gers = kwargs["gers"]
        if self.gers == "set()":
            self.gers = ""
        self.days = kwargs["days"]
        self.projectedE = int(kwargs["projectedE"])
        self.currentE = int(kwargs["currentE"])
        self.seats = int(kwargs["seats"])

        self.professorLast = self.professor.split(",")[0]

        empty = len(kwargs["times"]) == 0
        if not empty and '-' in kwargs["times"]:
            self.times = kwargs["times"]
            self.times = self.times.split('-')
            starttime = time.strptime(self.times[0], "%H%M")
            endtime = time.strptime(self.times[1], "%H%M")
            self.times = (starttime, endtime)
        elif not empty and kwargs["times"][0] == '(':
            self.times = kwargs["times"]
        else:
            self.times = tuple()

    def __eq__(self, other):
        return self.crn == other.crn and self.times == other.times

    def numeric_level(self):
        try:
            return int(self.level)
        except ValueError:
            return numeric(self.level)

    def oneline(self):
        pattern = "{}: {} w/ Prof. {} ({} {}-{}, CRN {})"
        return pattern.format(
            "OPEN" if self.isOpen else "CLOSED",
            self.title,
            self.professorLast,
            self.department,
            self.level,
            self.section,
            self.crn)

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
            self.crn)

    def fullinfo(self):
        try:
            humanTime = time.strftime("%I:%M %p", self.times[0]) \
                + " to " + time.strftime("%I:%M %p", self.times[1])
        except IndexError:
            humanTime = ''

        newline = "\n  "
        pattern =  "{} w/ Prof. {}"
        pattern += newline
        pattern += "{} ({} {}-{}, CRN {}); {} seat{} left"
        pattern += newline
        pattern += "{}{}{}"
        pattern += newline
        pattern += "fulfills {}"
        pattern += newline
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
            self.seats if self.seats != 0 else "no",
            's' if self.seats != 1 else '',
        # newline
            ", ".join(self.days) if self.days else "meeting",
            " from " if humanTime else " times TBA",
            humanTime,
        # newline
            "GER " + ", ".join(sorted(self.gers)) if self.gers else "no GERs",
        # newline
            self.creditHours,
            's' if self.creditHours != '1' else '',
            ": " if self.attributes else '',
            ", ".join(sorted(self.attributes)) if self.attributes else '')

    def toDict(self):
        timeTuple = self.times
        if len(timeTuple) == 2:
            timeTuple = (time.strftime("%H%M",self.times[0]),time.strftime("%H%M",self.times[1]))
        else:
            timeTuple = self.times
        return {
            "title": self.title,
            "crn": self.crn,
            "department": self.department,
            "isOpen": self.isOpen,
            "level": self.level,
            "section": self.section,
            "professor": self.professor,
            "creditHours": self.creditHours,
            "attributes": list(self.attributes), #TODO
            "gers": list(self.gers), #TODO
            "days": self.days,
            "projectedE": self.projectedE,
            "currentE": self.currentE,
            "seats": self.seats,
            "times": timeTuple}

    def toJSON(self):
        return json.dumps(self.toDict())

def numeric(alphanumeric):
    return int(''.join(c for c in alphanumeric if c.isdigit()))

def scrapeCourselist(termCode="201710") -> str:
    '''Outputs raw html scraped from <courselist.wm.edu>.'''

    url = "https://courselist.wm.edu/courselist/courseinfo/searchresults"
    payload = {
        "term_code": termCode,  # Defaults to Fall 2016
        "term_subj": "0",       # ALL
        "attr": "0",            # ALL
        "attr2": "0",           # ALL
        "levl": "0",            # ALL
        "status": "0",          # ALL
        "ptrm": "0",            # ALL
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

    crnPattern = r'<td.*>\s*<a[^>]*>([^<]+)</a>\s*</td>\s*'
    dataPattern = r'<td[^>]*>([^<]+)</td>\s*'
    fullPattern = re.compile(crnPattern + dataPattern * 11)
    return re.findall(fullPattern, htmlText)

def parseToCourseList(results: list(tuple())) -> list():
    '''
    Input is a list of tuples described in parseHtml().
    Output is a list of Course instances.
    '''

    openMap = {
        "OPEN": True,
        "CLOSED": False}

    weekdayMap = {
        'M': "Monday",
        'T': "Tuesday",
        'W': "Wednesday",
        'R': "Thursday",
        'F': "Friday"}

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
        tseats = int(result[10].strip('*'))

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
    courses = autoCourseList(True)
    astroCourses = list(filter(lambda x: x.department == "PHYS",courses))
    cDict = {}
    crns = []
    
    for i in astroCourses:
        print(str(i.crn) + ' ' + i.title + ' ' + str(i.times))
