from django.shortcuts import render


def homepage(request):
    return render(request, 'homepage.html')

def about_us(request):
    return render(request, 'about_us.html')

