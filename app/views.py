from email import message
import re
from ssl import SSLSession
from urllib import request
from wsgiref.util import request_uri
from django import template
from django.http import HttpResponseNotAllowed, HttpResponseRedirect, QueryDict
from django.shortcuts import get_object_or_404, render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.decorators.csrf import csrf_protect


"""
This views.py file contains actual server-side logic and frontend intergation.
"""


# Class ContentView is responsible for creating the objects and fetching the data from database : Handle get & post requests
class ContentView(View):

    """
    CBV :          get method & post method
    Render:        user-site.html Template
    search_params: title__icontains 
    """

    template_name = 'blog-manage.html'

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
class Update_View(View):

    """
    CBV:     Edit / Delete the Content\n
    Render:  update.html Template
    """
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


