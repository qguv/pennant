pennant
=======

(A course list which doesn't suck.)

A front-end for William and Mary's open course list system.

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
