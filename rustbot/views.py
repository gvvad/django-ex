from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(val):
    return HttpResponse("rustbot OK")
