#!/usr/bin/env python3
# vim:si:et:ts=4:sw=4

import re
import time
from course import Course


with open("results.html", 'r') as f:
    htmlText = f.read()

crnPattern = r'<td.*>\s*<a[^>]*>([^<]+)</a>\s*</td>\s*'
dataPattern = r'<td[^>]*>([^<]+)</td>\s*'
fullPattern = re.compile(crnPattern + dataPattern * 11)
results = re.findall(fullPattern, htmlText)

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

print()

for courseEntry in masterCourses:
    print(courseEntry.fullinfo())
