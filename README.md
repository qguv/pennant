pennant
=======

_"A course list which doesn't suck."_

A front-end API for William and Mary's course list system.

## Warning
In addition to the GPL, the [license] for this open-source API now mandates
that all derivative works do not scrape W&M's [courselist][] more than once
every five minutes. This is because the website is very weak, and the scraping
function `pb.scrapeCourselist()` puts noticeable strain on it.

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

To set up a server, you need a linux system with the following installed:

    Python >= 3.0
    Django 1.6
    mod_wsgi
    gunicorn

To install these, use your system's package manager, with the exception of
gunicorn. To install gunicorn, simply use:

    pip3 install gunicorn

Next, clone this repository to `wm`:

    git clone https://github.com/wm-pennant/pennant.git wm

Your directory structure should look like this:

    wm
    |____pennant
    |
    |____wm
    |
    |____manage.py
    |
    |____(other files)


In order to have data to read, you need to run the scraper script as follows:

    python3 quickfetch.py

**Note: The above script calls `scrapeCourselist()`, so do not call it more
than once every five minutes.**

Finally, to start the server, issue this command in the same directory as
`manage.py`:

    gunicorn wm.wsgi:application

Note: If you cannot connect to your server, try running it with:

    gunicorn -b 0.0.0.0:80 wm.wsgi:application

(May require root access to bind to port 80)

## Disclaimer

Please carefully read the [license][], which has recently changed.

[license]: https://github.com/wm-pennant/pennant/blob/master/LICENSE

This API uses only REST queries and does nothing you couldn't do with a
browser.
