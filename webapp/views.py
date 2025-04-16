from django.shortcuts import render, redirect

def index(request):
    if request.user.is_authenticated:
        # Check user groups and redirect accordingly
        if request.user.groups.filter(name="Techgrp").exists():
            return redirect('/admin')  # Admin dashboard
        elif request.user.groups.filter(name="Studentgrp").exists():
            return redirect('/student')  # Student dashboard
        elif request.user.groups.filter(name="Clubgrp").exists():
            return redirect('/club')  # Club dashboard
    
    return render(request, 'index.html')

def error(request):
    return render(request, 'error.html')

def error_404(request, exception):
    return render(request, 'error404.html')

def error_403(request, exception):
    return render(request, 'error403.html')
