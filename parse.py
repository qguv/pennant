#!/usr/bin/env python3
# vim:si:et:ts=4:sw=4

import re

with open("results.html","r") as f:
    text = f.read()
    
section_pattern = re.compile(r'<td.*>\s*<a[^>]*>([^<]+)</a>\s*</td>\s*' + r'<td[^>]*>([^<]+)</td>\s*' * 11)
result = re.search(section_pattern, text)

for i in range(1, 13):
    print(result.group(i))
