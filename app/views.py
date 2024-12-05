from email import message
import re
from ssl import SSLSession
from urllib import request
from wsgiref.util import request_uri
from django import template
from django.http import HttpResponseNotAllowed, HttpResponseRedirect, QueryDict
from django.shortcuts import get_object_or_404, render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate,login,logout
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import random
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
import time



"""
This views.py file contains actual server-side logic and frontend intergation.
"""


# Class ContentView is responsible for creating the objects and fetching the data from database : Handle get & post requests
class ContentView(LoginRequiredMixin,View):

    """
    CBV :          get method & post method
    Render:        user-site.html Template
    search_params: title__icontains 
    """

    template_name = 'blog-manage.html'
    login_url ='login-page'
    redirect_field_name = 'next'

    # Handle: Get Requests: list of Contents
    def get(self,request):

        # fetches the data from database
        queryset = Content.objects.all() 

        # Search option for content
        search_query = request.GET.get('search_re')
        if search_query:
            queryset= queryset.filter(title__icontains=search_query)

        # parse the context to render in .html
        context = {'Content': queryset}
        return render(request, self.template_name,context)
    
    # Handle post request : sends data to database
    def post(self,request):

        # posting data into database

        if request.method == 'POST':
            data = request.POST
            title = data.get("title")
            description = data.get("description")


            # creating the objects in database
            Content.objects.create(
                title=title,
                description=description,
            )

            print(
                f'Title: {title}\n Description: {description}\n'
            )


            return redirect('/user-site')
        

# class Update_View is responsible for editing the content that is already created in class ContentView: Handle get & post request
class Update_View(LoginRequiredMixin,View):

    """
    CBV:     Edit / Delete the Content\n
    Render:  update.html Template
    """
    login_url='login-page'

    # Handle: Get Requests: list of Contents
    def get(self,request,id):

        # get the object along with the id
        queryset= (
            Content.objects.get(id=id)
        )

        context = {"article": queryset}
        return render(request,'update.html',context)
    
    # Handle post request : sends data to database
    def post(self,request,id):

        queryset = Content.objects.get(id = id)

        # Handle post request

        if request.method == "POST":
            data = request.POST
            title = data.get("title")
            description = data.get("description")

            queryset.title = title
            queryset.description = description
            queryset.save()

            return redirect('user-site') 
        
# delete_page  is responsible for deleting the content from database compltely : Handle post request
@login_required(login_url='user-site')
def delete_page(request,id):

    queryset = Content.objects.get(id=id)
    queryset.delete()
    messages.success(request,"Thoughts has been deleted permanently")  

    return redirect('user-site')


# login_page is responsible for logging the user : Handle post request
class Loginpage(View):
    """
    Class-Based-View for user login
    """

    def get(self, request):
        """
        Handle the GET request and render the login page
        """
        # Redirect correctly to the login page (optional if you want to render)
        return render(request, 'login-page.html')

    def post(self, request):
        """
        Handle POST request: Authenticate user login
        """
        data = request.POST
        username = data.get("username")
        password = data.get("password")
        remember_me = data.get("remember_me") == 'on'

        # Check if user exists
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Handle remeber_me logic
            if remember_me:
                #session expiry in 30 days
                request.session.set_expiry(60*60*24*30)
            else:
                #default behaviour 
                request.session.set_expiry(0)
                
            return redirect('user-site')  # Redirect to user-site on successful login
        else:
            messages.error(request, "Invalid Username or Password")
        


        # Render login page with error message
        return render(request, 'login-page.html')
    
    
# SIgnUp is responsible for signing up the user with hashed password
class SignUp(View):
    """
    Handle User Credentials and store them safely in the database
    """

    def get(self, request):
        """
        Render sign-up.html
        """
        return render(request, 'sign-up.html')

    def post(self, request):
        """
        Handle the POST request for user registration.
        """
        data = request.POST
        firstname = data.get("firstname")
        lastname = data.get("lastname")
        username = data.get("username")
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        email = data.get("email")

        # Check if the user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "User Already Exists")
            return render(request, 'sign-up.html')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'sign-up.html')

        # Create the user if all validations pass
        user = User.objects.create(
            first_name=firstname,  
            last_name=lastname,    
            username=username,
            email=email
        )
        
        # Hash the password and save the user
        user.set_password(password)
        user.save()

        messages.success(request, "User created successfully.")
        return redirect('login-page')

    
# fx responsible for logout
def log_out(request):
    logout(request)
    return redirect('login-page')


#utility fx to  generate 4 digits otp
def generate_otp():
    """
    Generate 4 digit otp
    """
    return str(random.randint(1000,9999))

# CBV responsible for handeling forget_password request.
class forget_password(View):
    """
    CBV: Handle POST & GET Request\n
    Render the forget_password.html page
    """
    template_name = 'forget_password.html'

    # fx to handle the get Request
    def get(self,request):
        """
        Render the .html page
        """

        return render(request,self.template_name)
    
    def post(self,request):
        """
        Get the user input from the forms
        """

        if request.method == "POST":
            data = request.POST
            username = data.get("username")
            email = data.get("email")
        
        # user verification for otp
        if not User.objects.filter(username=username,email=email).exists:
            messages.error(request, f'Username or email does not exist')
            return render(request,self.template_name)
        
        # fx to generate 4 digit Otp
        otp = generate_otp()

        # storing the otp in sessions
        request.session['otp']=otp

        # Sending the otp to vaild user
        send_mail(

            subject="Request for OTP",
            message=f"You are seeing this mail because you request for the OTP.\n Your OTP is {otp}.",
            from_email="dronrajoffical@gmail.com",
            recipient_list=[email],
            fail_silently=False,
        )

        return redirect('verify-otp')
    

# CBV that verify the otp of the user
class Otpverfication(View):
    """
    CBV: Handle GET and POST Request
    """
    template_name = 'forget_password.html'

    def get(self,request):
        """
        Render the html page.
        """
        return render(request,self.template_name)
    
    def post(self,request):
        """
        Handle the POST requst and verify the session stored otp
        """
        data = request.post
        otp = data.get("otp")

        # check email otp against session

        session_otp = request.session.get('otp')

        print(session_otp)

        if session_otp != otp:
            message.error(request,"OTP Verification failed.")
            return render(request,self.template_name)
        
        # otp matches del otp from sessions
        del request.session['otp']

        return redirect('login-page') # for sure i will the login-page to reset password.


# setup the new forgetpage and verify page and reset-page then proceed the rest.


        

        

