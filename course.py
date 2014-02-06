#!/usr/bin/env python3
# vim:si:et:ts=4:sw=4

import time


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
        self.days = list(kwargs["days"])
        self.projectedE = int(kwargs["projectedE"])
        self.currentE = int(kwargs["currentE"])
        self.seats = int(kwargs["seats"])

        self.professorLast = self.professor.split(",")[0]

        if kwargs["times"] != '' and '-' in kwargs["times"]:
            self.times = kwargs["times"]
            self.times = self.times.split('-')
            starttime = time.strptime(self.times[0], "%H%M")
            endtime = time.strptime(self.times[1], "%H%M")
            self.times = (starttime, endtime)
        else:
            self.times = tuple()

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
        try:
            humanTime = time.strftime("%I:%M %p", self.times[0]) \
                + " to " + time.strftime("%I:%M %p", self.times[1])
        except IndexError:
            humanTime = ''

        pattern = "{} w/ Prof. {}\n    "
        pattern += "{} ({} {}-{}, CRN {})\n    "
        pattern += "{}{}{}"
        pattern += "fulfills {}\n    "
        pattern += "{} credit{}{}{}\n"
        return pattern.format(
            self.title,
            self.professorLast,
        # newline
            "OPEN" if self.isOpen else "CLOSED",
            self.department,
            self.level,
            self.section,
            self.crn,
        # newline
            ", ".join(self.days) if self.days else '',
            " from " if self.days and humanTime else \
                "meets from " if humanTime else '',
            humanTime + "\n    " if self.days or humanTime else '',
        # newline
            "GER " + ", ".join(sorted(self.gers)) if self.gers else "no GERs",
        # newline
            self.creditHours,
            's' if self.creditHours != '1' else '',
            ": " if self.attributes else '',
            ", ".join(sorted(self.attributes)) if self.attributes else '',
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
        times="1400-1520",
        projectedE=40,
        currentE=39,
        seats=1,
    )
    print("Data Structures Course, standard output:\n\n", dataStructures, "\n\n")
    print("Data Structures Course, oneline:\n\n", dataStructures.oneline(), "\n\n")
    print("Data Structures Course, fullinfo:\n\n", dataStructures.fullinfo())
