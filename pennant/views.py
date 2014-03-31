from django.shortcuts import render
from django.http import HttpResponse

import pennant.backend
import sqlite3

# Create your views here.

def index(request):
    return render(request, 'index.html', {})


def getlist(request):
    courseList = pennant.backend.autoCourseList(True)
    #Should be the name of the department
    department = request.GET.get('department')
    if department is not None:
        courseList = list(filter(lambda x: x.department == department,courseList))

    jsonList = []
    for course in courseList:
        jsonList.append(course.toJSON())
    resultStr = '{\"courses\":['
    for jcourse in jsonList:
        resultStr += jcourse + ","
    resultStr = resultStr[:len(resultStr) - 1]
    resultStr += "]}"

    return render(request, 'getJSON.html', {'courseList':resultStr})

def jsonpcallback(request):
    courseList = pennant.backend.autoCourseList(True)
    #Should be the name of the department
    callbackName = request.GET.get('callback')
    if callbackName is None:
        callbackName = 'jsonpcallback'

    jsonList = []
    for course in courseList:
        jsonList.append(course.toJSON())
    resultStr = callbackName + '({\"courses\":['
    for jcourse in jsonList:
        resultStr += jcourse + ","
    resultStr = resultStr[:len(resultStr) - 1]
    resultStr += "]});"

    return render(request, 'getJSON.html', {'courseList':resultStr})

