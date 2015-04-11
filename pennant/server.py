#!/usr/bin/env python3
# vim:si:et:ts=4:sw=4

import backend as pb

from flask import Flask, jsonify, abort
app = Flask(__name__)

from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()

ONE_PAGE = 30 # items

def everything(toDict=False):
    everything = cache.get('everything')
    if everything is None:
        with open("results.html") as f:
            everything = pb.parseToCourseList(pb.parseHtml(pb.scrapeCourselist()))
        minutes = 60 # constant
        cache.set('everything', everything, timeout=5*minutes)

    if toDict:
        return [ course.toDict() for course in everything ]

    return everything

def coursesByProperty(func, onlyOne=False, toDict=False):

    assemble = list

    # if there's the potential for duplicate courses (current work-around for
    # multiple-session courses with CRN), ignore all but the first result
    # TODO: properly combine courses with multiple meeting times
    if onlyOne:
        assemble = next

    # to abstract over single-course dictionary-making and multi-course
    # dictionary-making, we deal with the following special cases:
    convert = assemble

    # there's only one course result
    if toDict and onlyOne:
        convert = lambda x: assemble(x).toDict()

    # there are many course results
    elif toDict:
        convert = lambda x: [ course.toDict() for course in assemble(x) ]

    try:
        f = filter(func, everything())
        return convert(f)
    except IndexError:
        abort(404)

def singleJSON(singleton):
    return jsonify(**singleton)

def multiJSON(name, sequence):
    return jsonify(**{name: sequence})

def pagedJSON(name, sequence, page):
    '''One-indexes.'''

    seqlen = len(sequence)
    pages = seqlen // ONE_PAGE + 1

    first = (page - 1) * ONE_PAGE
    afterLast = first + ONE_PAGE

    if first >= seqlen or page < 1:
        abort(404)

    if afterLast >= seqlen:
        afterLast = -1

    return jsonify(**{name: sequence[first:afterLast], "page": page, "pages": pages})

@app.route('/allcourses/', defaults={'page': 1})
@app.route('/allcourses/page/<int:page>')
def allcourses(page):
    return pagedJSON("courses", [ course.toDict() for course in everything() ], page)

@app.route("/courses/<int:crn>")
@app.route("/courses/crn/<int:crn>")
@app.route("/courses/CRN/<int:crn>")
def courseByCRN(crn):
    return singleJSON(coursesByProperty(lambda x: x.crn == crn, onlyOne=True, toDict=True))

@app.route("/courses/department/<department>/", defaults={'page': 1})
@app.route("/courses/department/<department>/page/<int:page>")
def coursesByDepartment(department, page):
    return pagedJSON("courses", coursesByProperty(lambda x: x.department == department, toDict=True), page)

if __name__ == "__main__":
    app.run(debug=True)
