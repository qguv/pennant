#!/usr/bin/env python3
# vim:si:et:ts=4:sw=4

import re
import time
from course import Course


with open("results.html","r") as f:
    text = f.read()
    
section_pattern = re.compile(r'<td.*>\s*<a[^>]*>([^<]+)</a>\s*</td>\s*' + r'<td[^>]*>([^<]+)</td>\s*' * 11)
results = re.findall(section_pattern, text)

#testRes = results[1];

opnMap = {"OPEN":True,"CLOSED":False}
weekDays = {"M":"Monday","T":"Tuesday","W":"Wendsday","R":"Thursday","F":"Friday"}


masterCourses = []


#for attr in testRes:
    #print(attr)

for testRes in results:
    topn = opnMap[testRes[11]]
    tcrn = testRes[0]

    titleData = testRes[1].split(" ")
    tdepart = titleData[0]
    tlevel = titleData[1]
    tsection = titleData[2]

    ttitle = testRes[3]
    ttitle = ttitle.replace("&amp;","&")

    tprof = testRes[4]
    tcredit = testRes[5]

    tattrs = set()
    tgers = set()
    if testRes[2] != "":
        attribs = testRes[2].split(", ")
        for attrib in attribs:
            if "GE" in attrib:
                tgers.add(attrib)
            else:
                tattrs.add(attrib)

    days = testRes[6]
    tdays = set()
    if days != "":
        for d in days:
            if d in "MTWRF":
                tdays.add(weekDays[d])


    ttime = ("","")
    if testRes[7] != "" and '-' in testRes[7]:
        ttimes = testRes[7].split("-")
        starttime = time.strptime(ttimes[0],"%H%M")
        endtime = time.strptime(ttimes[1],"%H%M")
        ttime = (starttime,endtime)

    tprojectede = int(testRes[8])
    tcurrente = int(testRes[9])
    tseats = int(testRes[10])

    someCourse = Course(isOpen=topn,crn=tcrn,department=tdepart,level=tlevel,section=tsection,title=ttitle,professor=tprof,creditHours=tcredit,attributes=tattrs,gers=tgers,days=tdays,times=ttime,projectedE=tprojectede,currentE=tcurrente,seats=tseats)

    masterCourses.append(someCourse)

print()

for i in range(len(masterCourses)):
    print(masterCourses[i])

#for result in results:
    #for attr in result:
        #print(attr)
