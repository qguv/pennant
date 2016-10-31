#!/usr/bin/env python3

import pennant.backend as pb
import json
from datetime import datetime

courses = []

print("Getting departments...", end='', flush=True)
departments = pb.get_departments()
print(" OK")

for ident, name in pb.get_departments().items():
    print("Getting courses in {}...".format(name), end='', flush=True)
    courses.extend(pb.scrape_department(ident))
    print(" OK")

stamp = datetime.now().strftime("%Y_%m_%d")
filename = "results_{}.json".format(stamp)

print("Writing {} courses to file '{}'...".format(len(courses), filename), end='', flush=True)
with open(filename, "w+") as f:
    json.dump(courses, f)
print(" OK")
