pennant
=======

_"A course list which doesn't suck."_

A front-end for William and Mary's open course list system.

## Warning
Please don't call pb.scrapeCourselist() too often. W&M's [courselist][] website
is very weak and the function puts quite a bit of strain on it. Don't get us in
trouble; scrape no more than once every five minutes, and be sure to offset.

[courselist]: https://courselist.wm.edu/

## Example usage

```python
$ python3 -Biq
>>> import pennant.backend as pb
>>> rawHtml = pb.scrapeCourselist()
>>> courses = pb.parseToCourseList(pb.parseHtml(rawHtml))
>>> for course in courses[:3]:
...     print(course.fullinfo())
...
Black Speculative Arts w/ Prof. Sanford
    OPEN (AFST 150-01, CRN 29786)
    Tuesday, Thursday from 12:30 PM to 01:50 PM
    fulfills no GERs
    3 credits: FRSM

Black&White in American Drama w/ Prof. Weiss
    OPEN (AFST 150W-01, CRN 30028)
    Tuesday, Thursday from 09:30 AM to 10:50 AM
    fulfills no GERs
    4 credits: FRSM, LDWR

Intro to Africana Studies w/ Prof. Osiapem
    OPEN (AFST 205-01, CRN 29007)
    Monday, Wednesday from 03:30 PM to 04:50 PM
    fulfills GER 4C, 5
    3 credits

>>> print(courses[0].title, "is", "open" if courses[0].isOpen else "closed")
Black Speculative Arts is open
>>> "Thursday" in courses[0].days
True
>>>

```

## Setting Up a Server

To set up a server, you need a linux system with the following installed
```
    Python >= 3.0
    Django 1.6
    mod_wsgi
    gunicorn
```
To install these, use your system's package manager, with the exception of gunicorn. To install gunicorn, simply use:
    ```
    pip3 install gunicorn
    ```
