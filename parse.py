#!/usr/bin/env python3
# vim:si:et:ts=4:sw=4

import re

with open("results.html","r") as f:
    text = f.read()
    
section_pattern = re.compile(r'<td.*>\s*<a[^>]*>([^<]+)</a>\s*</td>\s*' + r'<td[^>]*>([^<]+)</td>\s*' * 11)
results = re.findall(section_pattern, text)

for result in results:
    for attr in result:
        print(attr)
