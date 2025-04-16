from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
import traceback
import pyrebase
import os

# Firebase configuration
firebaseConfig = settings.FIREBASE_CONFIG

try:
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()
except Exception as e:
    print(f"Firebase initialization error: {str(e)}")
    auth = None

# Import data handlers after all other imports
from student.datahandler import StudentDataHandler
from club.datahandler import ClubDataHandler

def loginuser(request):
    if request.user.is_authenticated:
        try:
            return redirect(request.GET.get('next'))
        except:
            return redirect("/")

    if request.method == 'POST':
        email = request.POST['username']
        password = request.POST['password']
        login_type = request.POST.get('login_type', 'user')
        
        try:
            if login_type == 'admin':
                # For admin login, try Django's authentication first
                if email == "admin@example.com":
                    # Use 'admin' as username instead of email for authentication
                    user = authenticate(username='admin', password=password)
                    if user is not None and user.groups.filter(name="Techgrp").exists():
                        login(request, user)
                        return redirect("/club")
                    else:
                        return render(request, 'login.html', {'alert': 1, 'error': 'Invalid admin credentials'})
                else:
                    return render(request, 'login.html', {'alert': 1, 'error': 'Invalid admin email'})
            else:
                # Regular user login with Firebase
                if auth is None:
                    return render(request, 'login.html', {'alert': 1})
                    
                # Try Firebase authentication for regular users
                user = auth.sign_in_with_email_and_password(email, password)
                user = authenticate(username=user['localId'], password="deZE%KYzH5jVBbHN")
                
                if user is not None:
                    login(request, user)
                    if user.groups.filter(name="Studentgrp").exists():
                        return redirect("/student")
                    else:
                        return render(request, 'login.html', {'alert': 1, 'error': 'You do not have student access'})
                else:
                    return render(request, 'login.html', {'alert': 1})
        except Exception as e:
            print(f"Login error: {str(e)}")
            return render(request, 'login.html', {'alert': 1})
    return render(request, 'login.html')


def signup(request):
    if request.user.is_authenticated:
        try:
            return redirect(request.GET.get('next'))
        except:
            return redirect("/")

    if request.method == 'POST':
        studentId = request.POST['id']
        studentName = request.POST['name']
        studentEmail = request.POST['email']
        password = request.POST['password']
        studentData = {"studentId" : studentId , "studentName" : studentName ,"studentEmail" : studentEmail}
        status = studata.createStudent(studentData,password)
        if status is None:
            return HttpResponse(status = 500)
        else:
            return render(request , 'thankyou.html')

    return render(request , 'signup.html') 

def logoutuser(request):
    if request.user.is_authenticated:
        logout(request)
        return render(request , 'logout.html')
    else:
        return redirect('/user/login/')


@login_required(login_url = '/user/login/')
def changepassword(request):
    try:
        userEmail = request.user.email
        auth.send_password_reset_email(userEmail)
        logout(request)
        return render(request , 'changepassword.html')
    except:
        traceback.print_exc()
        return HttpResponseServerError()
    

@login_required(login_url = '/user/login/')
def loadprofile(request):
    if request.user.groups.filter(name = "Studentgrp").exists():
        id = request.user.username
        studentData = studata.getStudent(id)
        if studentData is None:
            raise Http404()
        
        context = {"studentData" : studentData}
        return render(request , 'studentprofile.html' , context)
    
    elif request.user.groups.filter(name = "Clubgrp").exists():
        if request.method == 'POST':
            if request.POST['action'] == "Update":
                clubname = request.POST.get('clubName')
                clubemail = request.POST.get('clubEmail')
                clubDescription = request.POST.get('clubDescription')
                clubImgUrl = request.POST.get('imgUrl')
                ClubData = {"clubName" : clubname , "clubEmail" : clubemail , "clubDescription" : clubDescription , "clubImgUrl" : clubImgUrl}
                ClubData["discordLink"] =  request.POST.get('discordLink')
                ClubData["instaLink"] =  request.POST.get('instaLink')
                ClubData["linkedinLink"]  =  request.POST.get('linkedinLink')
                ClubData["telegramLink"] =  request.POST.get('telegramLink')
                ClubData["twitterLink"] =  request.POST.get('twitterLink')
                ClubData["whatsappLink"] =   request.POST.get('whatsappLink')
                ClubData["youtubeLink"] =  request.POST.get('youtubeLink')

                try:
                    clubdata.updateClub(request.user.username , ClubData)
                except:
                    traceback.print_exc()
                    return HttpResponseServerError()

        id = request.user.username
        data = clubdata.getClub(id)
        if data is None:
            raise Http404()
        
        context = {"club" : data}
        return render(request , 'clubprofile.html' , context)

    elif request.user.groups.filter(name = "Techgrp").exists():
        return redirect("/admin")
    
    else:
        return HttpResponseForbidden()


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            if auth is None:
                return render(request, 'forgot_password.html', {'alert': 'Firebase not initialized'})
            auth.send_password_reset_email(email)
            return render(request, 'forgot_password.html', {'success': True})
        except Exception as e:
            print(f"Password reset error: {str(e)}")
            return render(request, 'forgot_password.html', {'alert': 'Invalid email address'})
    return render(request, 'forgot_password.html')