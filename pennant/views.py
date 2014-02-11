from django.shortcuts import render
from django.http import HttpResponse

import pennant.backend

# Create your views here.

def index(request):
    courseList = pennant.backend.autoCourseList()
    return render(request, 'pennant/test.html', {'courseList':courseList})

def getlist(request):
    courseList = pennant.backend.autoCourseList()
    jsonList = []
    for course in courseList:
        jsonList.append(course.toJSON())
    resultStr = '{\"masterList\":['
    for jcourse in jsonList:
        resultStr += jcourse + ","
    resultStr = resultStr[:len(resultStr) - 1]
    resultStr += "]}"

    return render(request, 'pennant/getJSON.html', {'courseList':resultStr})
