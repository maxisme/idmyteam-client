from django.shortcuts import render
from idmyteam import helpers

# Create your views here.
def welcome_handler(request):
    return render(request, "home/welcome.html")