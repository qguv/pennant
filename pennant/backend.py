#!/usr/bin/env python3
# vim:si:et:ts=4:sw=4

import html
import json
import re
from textwrap import dedent, wrap
import requests
import time

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

def sort_by_scarcity(courses, reverse=False):
    return sorted(courses, key=lambda c: c.seats, reverse=reverse)

def collapse_spaces(s):
    return ' '.join(s.split())

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
        if self.days:
            meeting = ", ".join(self.days)
        else:
            meeting = "meeting"

        try:
            to_ht = lambda x: time.strftime("%I:%M %p", x)
            start, end = self.times[0:2]
            meeting += " from {} to {}".format(to_ht(start), to_ht(end))
        except (ValueError, SyntaxError): # not enough values to unpack
            meeting += " times TBA"

        return "\n  ".join([

            "{} {}-{}: {} w/ Prof. {}".format(
                self.department,
                self.level,
                self.section,
                self.title,
                self.professorLast,
            ),

            meeting,

            "{}: {} spot{} left (space for {})".format(
                "OPEN" if self.isOpen else "CLOSED",
                self.seats if self.seats != 0 else "no",
                's' if self.seats != 1 else '',
                self.currentE + self.seats,
            ),

            "{} credit{}, fulfills {}".format(
                self.creditHours,
                's' if self.creditHours != '1' else '',
                ("GER " + ", ".join(sorted(self.gers)) if self.gers else "no GERs"),
            ),

            "CRN {}".format(self.crn),

        ]) + '\n'

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

    def generate_email(self, name=None, student_id=None, social_class=None, major=None):

        if not self.isOpen:
            problem = "the section is closed"
        else:
            problem = "I was unable to add the course"

        header = """\
        To: {0.professor}
        Subject: [{0.department} {0.level}-{0.section}] Closed Section Override Request

        Dear Professor {0.professorLast},
        """

        footer = """\
        Kind regards,
        {name}
        {student_id}
        """

        body = """\
        I am a {social_class} majoring in {major}. I was planning to take
        {0.department} {0.level}, section {0.section} (CRN {0.crn}) this
        semester, but unfortunately {problem}. Would it be possible to get an
        override?
        """

        header = dedent(header.format(self))
        footer = dedent(footer.format(name=name, student_id=student_id))
        body_lines = wrap(dedent(body.format(self,
            social_class=social_class,
            major=major,
            problem=problem
        )))
        return "{}\n{}\n\n{}".format(header, '\n'.join(body_lines), footer)

    @classmethod
    def from_tuple(cls, c: tuple) -> 'Course':
        '''
        Input is a list of tuples described in parse_department().
        Output is a list of Course instances.
        '''

        weekdays = {
            'M': "Monday",
            'T': "Tuesday",
            'W': "Wednesday",
            'R': "Thursday",
            'F': "Friday",
            'S': "Saturday",
            'U': "Sunday"}

        dept, level, section = c[1].split(" ")

        tattrs = set()
        tgers = set()
        if c[2] != '':
            attribs = c[2].split(", ")
            for attrib in attribs:
                if "GE" in attrib:
                    tgers.add(attrib[2:])
                elif "&nbsp;" in attrib:
                    continue
                elif attrib in ('.'):
                    continue
                else:
                    tattrs.add(attrib)

        if c[7] != '' and '-' in c[7]:
            ttime = c[7]
        else:
            ttime = tuple()

        tprojectede = int(c[8])
        tcurrente = int(c[9])
        tseats = int(c[10].strip('*'))

        return cls(isOpen='OPEN' == c[11],
                   crn=c[0],
                   department=dept,
                   level=level,
                   section=section,
                   title=c[3],
                   professor=c[4],
                   creditHours=c[5],
                   attributes=tattrs,
                   gers=tgers,
                   days=[weekdays[d] for d in c[6]],

                   times=ttime,
                   projectedE=tprojectede,
                   currentE=tcurrente,
                   seats=tseats)

def get_departments() -> [str]:

    url = "https://courselist.wm.edu/courselist/"
    r = requests.post(url)
    r.raise_for_status()
    src = r.text

    begin = src.find('id="term_subj"')
    end = src.find('</select>', begin)
    region = src[begin:end]

    course_pattern = re.compile(r'<option value="([^"]+?)" >([^<]+?)</option>')
    matches = course_pattern.finditer(region)

    # ignore the first match, the 'ALL' default
    next(matches)

    return dict((html.unescape(group) for group in match.groups())
                 for match in matches)

def scrape_department(department, term_code="201720") -> 'html':
    '''
    result tuples have have the following format:
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

    # create the request
    url = "https://courselist.wm.edu/courselist/courseinfo/searchresults"
    payload = {
        "term_code": term_code, # Defaults to Spring 2017
        "term_subj": department,
        "attr": "0",            # ALL
        "attr2": "0",           # ALL
        "levl": "0",            # ALL
        "status": "0",          # ALL
        "ptrm": "0",            # ALL
    }

    r = requests.post(url, payload)
    r.raise_for_status()
    src = r.text.replace("\r", "\n")

    crn = r'<td.*>\s*<a[^>]*>([^<]+)</a>\s*</td>\s*'
    course_datum = r'<td[^>]*>([^<]+)</td>\s*'
    pattern = re.compile(crn + course_datum * 11)
    dirty = pattern.findall(src)
    clean = [[collapse_spaces(html.unescape(datum)) for datum in course]
             for course in dirty]

    return clean
