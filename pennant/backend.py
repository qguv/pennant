#/usr/bin/env python3
# vim:si:et:ts=4:sw=4

import time
import json
import sqlite3

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

        if kwargs["times"] != '' and '-' in kwargs["times"]:
            self.times = kwargs["times"]
            self.times = self.times.split('-')
            starttime = time.strptime(self.times[0], "%H%M")
            endtime = time.strptime(self.times[1], "%H%M")
            self.times = (starttime, endtime)
        elif kwargs["times"] != '' and kwargs["times"][0] == '(':
            self.times = kwargs["times"]
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
            timeTuple = self.times
        jsonStr = json.dumps({"isOpen":self.isOpen,"crn":self.crn,"title":self.title,"department":self.department,"level":self.level,"section":self.section,"professor":self.professor,"creditHours":self.creditHours,"attributes":self.attributes,"gers":self.gers,"days":self.days,"projectedE":self.projectedE,"currentE":self.currentE,"seats":self.seats,"times":timeTuple})
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
        "term_code": "201510",  # Fall 2014
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


def setupDB():
    db = sqlite3.connect('courses.db')

    c = db.cursor()

    c.execute('''create table courses (isopen integer,crn integer,department text,level text,section text,title text,professor text,credithours text,attributes text,gers text,days text,projectedE integer,currentE integer,seats integer,times text)''');

    db.commit()

    c.close()

def toDB():
    with open("results.html",'r') as f:
        rawHtml = f.read()

    parsedHtml = parseHtml(rawHtml)
    courseList = parseToCourseList(parsedHtml)

    db = sqlite3.connect('courses.db')

    c = db.cursor()

    for course in courseList:
        if len(course.times) != 0:
            sqlString = "insert into courses values ({})".format(','.join([str(int(course.isOpen)), str(course.crn), '"' + course.department + '"', '"' + course.level + '"', '"' + course.section + '"', '"' + course.title + '"', '"' + course.professor + '"','"' + str(course.creditHours) + '"', '"' + str(course.attributes) + '"','"' +  str(course.gers) + '"', '"' + str(course.days) + '"', str(course.projectedE), str(course.currentE), str(course.seats), '"' + str((time.strftime("%H%M",course.times[0]),time.strftime("%H%M",course.times[1]))) + '"']))
        else:
            sqlString = "insert into courses values ({})".format(','.join([str(int(course.isOpen)), str(course.crn), '"' + course.department + '"', '"' + course.level + '"', '"' + course.section + '"', '"' + course.title + '"', '"' + course.professor + '"','"' + str(course.creditHours) + '"', '"' + str(course.attributes) + '"','"' +  str(course.gers) + '"', '"' + str(course.days) + '"', str(course.projectedE), str(course.currentE), str(course.seats), '""']))

        print(sqlString)
        c.execute(sqlString)
    
    db.commit()

    c.close()


def autoCourseList(useDB) -> list():
    if useDB == False:
        with open("results.html", 'r') as f:
            rawHtml = f.read()

        parsedHtml = parseHtml(rawHtml)
        courseList = parseToCourseList(parsedHtml)
    
        return courseList
    else:
        courseList = []

        db = sqlite3.connect('courses.db')

        c = db.cursor()

        c.execute("select * from courses")

        for item in c:
            courseList.append(Course(isOpen=item[0],crn=item[1],department=item[2],level=item[3],section=item[4],title=item[5],professor=item[6],creditHours=item[7],attributes=item[8],gers=item[9],days=item[10],projectedE=item[11],currentE=item[12],seats=item[13],times=item[14]))
            print(item)

        cDict = {}
        for i in range(len(courseList)):
            x = courseList[i]
            if str(x.crn) in cDict:
                cDict[str(x.crn)].times += "," + str(x.times)
                courseList[i] = cDict[str(x.crn)]
            else:
                cDict[str(x.crn)] = x
        courseList = []
        for item in cDict:
            if item not in courseList:
                courseList.append(cDict[item])


        return courseList


if __name__ == "__main__":
    #print("Setting up DB...")
    #setupDB()
    #toDB()
    courses = autoCourseList(True)
    astroCourses = list(filter(lambda x: x.department == "PHYS",courses))
    cDict = {}
    crns = []
    
    for i in astroCourses:
        print(str(i.crn) + ' ' + i.title + ' ' + str(i.times))
