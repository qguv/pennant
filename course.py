#!/usr/bin/env python3
# vim:si:et:ts=4:sw=4

from datetime import time


class Course:

    def __init__(self, **kwargs):
        self.isOpen = bool(kwargs["isOpen"])
        self.crn = int(kwargs["crn"])
        self.department = str(kwargs["department"])
        self.level = str(kwargs["level"])
        self.section = str(kwargs["section"])
        self.title = str(kwargs["title"])
        self.professor = str(kwargs["professor"])
        self.creditHours = str(kwargs["creditHours"])
        self.attributes = set(kwargs["attributes"])
        self.gers = set(kwargs["gers"])
        self.days = set(kwargs["days"])
        self.times = tuple(kwargs["times"])
        self.projectedE = int(kwargs["projectedE"])
        self.currentE = int(kwargs["currentE"])
        self.seats = int(kwargs["seats"])

    def __str__(self):
        pattern = "{0}-{1}-{2}\t{3}\t    {4}\t{5}"
        return pattern.format(
            self.department,
            self.level,
            self.section,
            self.title,
            self.professor,
            str(self.isOpen))


if __name__ == "__main__":
    dataStructures = Course(
        isOpen=True,
        crn=12345,
        department="CSCI",
        level="241",
        section=1,
        title="Data Structures",
        professor="Dickerson, Robert F.",
        creditHours="3",
        attributes={},
        gers={},
        days={"Monday", "Wendsday"},
        times=(time(14, 0), time(15, 20)),
        projectedE=40,
        currentE=39,
        seats=1,
    )
    print(dataStructures)
