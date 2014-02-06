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
        self.professorLast = self.professor.split(",")[0]

    def oneline(self):
        pattern = "{}: {} w/ Prof. {} ({} {}-{}, CRN {})"
        return pattern.format(
            "OPEN" if self.isOpen else "CLOSED",
            self.title,
            self.professorLast,
            self.department,
            self.level,
            self.section,
            self.crn,
        )

    def __str__(self):
        pattern = "{} w/ Prof. {}\n"
        pattern += "    {} ({} {}-{}, CRN {})\n"
        return pattern.format(
            self.title,
            self.professorLast,
            "OPEN" if self.isOpen else "CLOSED",
            self.department,
            self.level,
            self.section,
            self.crn,
        )

    def fullinfo(self):
        pattern = "{} w/ Prof. {}\n"
        pattern += "    {} ({} {}-{}, CRN {})\n"
        pattern += "    {} credit{}{}{}\n"
        return pattern.format(
            self.title,
            self.professorLast,
            "OPEN" if self.isOpen else "CLOSED",
            self.department,
            self.level,
            self.section,
            self.crn,
            self.creditHours,
            "s" if self.creditHours != '1' else "",
            ": " if self.attributes else "",
            ", ".join(sorted(self.attributes)) if self.attributes else "",
        )

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
