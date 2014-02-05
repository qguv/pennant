#!/usr/bin/env python3
# vim:si:et:ts=4:sw=4

class Course:
    def __init__(self, **kwargs):
        self.isOpen = kwargs["open"]
        self.crn = kwargs["crn"]
        self.department = kwargs["department"]
        self.level = kwargs["level"]
        self.gers = kwargs["gers"]



