#!/usr/bin/env python3
# vim:si:et:ts=4:sw=4

import re
from course import Course

with open("results.html","r") as f:
    text = f.read()
    
section_pattern = re.compile(r'<td.*>\s*<a[^>]*>([^<]+)</a>\s*</td>\s*' + r'<td[^>]*>([^<]+)</td>\s*' * 11)
results = re.findall(section_pattern, text)

testRes = results[1];

opnMap = {"OPEN":True,"CLOSED":False}
weekDays = {"M":"Monday","T":"Tuesday","W":"Wendsday","R":"Thursday","F":"Friday"}


for attr in testRes:
    print(attr)


topn = opnMap[testRes[11]]
tcrn = testRes[0]

titleData = testRes[1].split(" ")
tdepart = titleData[0]
tlevel = titleData[1]
tsection = int(titleData[2])

ttitle = testRes[3]
tprof = testRes[4]
tcredit = testRes[5]

attribs = testRes[2].split(", ")
tattrs = {}
tgers = {}
for attrib in attribs:
    if "GE" in attrib:
        tgers.add(attrib)
    else:
        tattrs.add(attrib)

days = testRes[6]
tdays = {}
if days != "":
    for d in days:
        tdays.add(weekDays[d])


ttime = ("","")
if testRes[7] != "":
    ttimes = testRes[7].split("-")
    starttime = strptime(ttimes[0],"%H%M")
    endtime = strptime(ttimes[1],"%H%M")
    ttime = (starttime,endtime)


#for result in results:
    #for attr in result:
        #print(attr)
