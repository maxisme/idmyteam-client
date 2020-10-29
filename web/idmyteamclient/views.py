from django.shortcuts import render


def welcome_handler(request):
    return render(request, "home/welcome.html")
