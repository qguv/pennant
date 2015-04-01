#!/usr/bin/env python3

import pennant.backend

print("Retrieving course list...")
pennant.backend.writeCourselist("results.html")
print("Done")
