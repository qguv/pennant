#!/usr/bin/env python3
# vim:si:et:ts=4:sw=4

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

with open("results.html", 'w') as f:
    f.write(response)
