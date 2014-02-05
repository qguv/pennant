#!/usr/bin/env python3

import requests

payload = {
    "term_code" :   "201420",   #Spring 2014
    "term_subj" :   "0",        #ALL
    "attr"      :   "0",        #ALL
    "levl"      :   "0",        #ALL
    "status"    :   "0",        #ALL
}

r = requests.post("https://courselist.wm.edu/courseinfo/searchresults", payload)

with open("results.html", 'w') as f:
    response = r.text.replace("", "")
    f.write(r.text)

