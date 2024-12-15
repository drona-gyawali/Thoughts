from email import message
import re
from ssl import SSLSession
from urllib import request
from wsgiref.util import request_uri
from django import template
from django import views
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
        queryset = Content.objects.filter(user=request.user) 

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
                user= request.user,
                title=title,
                description=description,
            )

            messages.success(request,"Content created.")


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
            messages.success(request,'Content Edited')

            return redirect('user-site') 


        
# delete_page  is responsible for deleting the content from database compltely : Handle post request
@login_required(login_url='user-site')
def delete_page(request,id):

    try:
        queryset = Content.objects.get(id=id)
        queryset.delete()
        messages.warning(request,"Content Deleted")
        return redirect('user-site')
    except Content.DoesNotExist:
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
                
            return redirect('/')  
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
        image = request.FILES.get('profile_image')

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
            email=email,
        )
        
        # Hash the password and save the user
        user.set_password(password)
        user.save()

        if not hasattr(user, 'profile'):
            profile = Profile.objects.create(user=user)

        # Now, update the profile image if provided
        if image:
            profile.image = image
            profile.save()

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
        if not User.objects.filter(username=username,email=email).exists():
            messages.error(request, 'Username or email does not exist')
            return render(request,self.template_name)
        
        # fx to generate 4 digit Otp
        otp = generate_otp()

        # storing the otp and usrname in sessions
        request.session['otp']=otp
        request.session['username']=username


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
    template_name = 'verify-otp.html'

    def get(self,request):
        """
        Render the html page.
        """
        return render(request,self.template_name)
    
    def post(self,request):
        """
        Handle the POST requst and verify the session stored otp
        """
        data = request.POST

        # geting the user input otp
        otp = "".join([
            data.get("otp1", ""),
            data.get("otp2", ""),
            data.get("otp3", ""),
            data.get("otp4", "")
        ])

        # check email otp against session

        session_otp = request.session.get('otp')


        if session_otp != otp:
            messages.error(request,"OTP Verification failed.")
            return render(request,self.template_name)
        
        #get the username form session
        username=request.session.get('username')
        

        return redirect('reset-password',username=username) 
    
    
# CBV : Handle  reset password request.
class ResetPassword(View):
    """
    Handle get and post request and reset the password of user.
    """
    template_name = 'reset_password.html'

    def get(self,request,username):
        """
        render the page.
        """

        # ensure user has the otp: flag for unothorized access
        if not request.session.get('otp'):
            return redirect('login-page')


        queryset = User.objects.get(username = username)


        context = {'username': queryset}

        return render(request, self.template_name, context)
    
    def post(self,request,username):
        """
        Handle POST Logic.
        """

        user = User.objects.get(username=username)

        data = request.POST
        password = data.get('new-password')
        confirm_password = data.get('confirm-password')

        # check if password is correct
        if password != confirm_password:
            messages.error(request,'Password_doesnot match')
            return render(request,self.template_name)
        
        user.set_password(password)
        user.save()

        #clear session data
        request.session.pop('otp',None)
        request.session.pop('username',None)

        return redirect('login-page',)


class SocialView(LoginRequiredMixin,View):
    """
    This CBV is responsible for the social interface: User Interaction Environment
    """

    template_name = 'social.html'
    login_url= 'login-page'
    redirect_field_name='user'

    def get(self, request):
        """
        Render the Web page and fetch the data
        """
        # Fetching the content by latest date.
        queryset = Content.objects.all().order_by('-created_at')


        # Search functionality where user can search the username
        search_params = request.GET.get('search_me')

        if search_params:  # If a search query exists
            # Filter users by username
            users = User.objects.filter(username__icontains=search_params)
            queryset = Content.objects.filter(user__in=users)

        user = User.objects.all()
        # Pass the filtered or default content to the template
        context = {'content': queryset, 'users':user}
        return render(request, self.template_name, context)
    
    def post(self,request):
        """
        Handle the POST for comments
        """

        if request.method == "POST":
            data = request.POST
            # hidden id request to know post refrence
            try:
                content_id = data.get('content_id')
                # finding the post by its id
                content = Content.objects.get(id = content_id)
            except content.DoesNotExist:
                messages.error(request, 'Content is not anymore.')
                return redirect('/')
            

            # Getting the comment from the text
            comment = data.get('comment')

            try:
                new_comment = Comment.objects.create(

                    comment=comment,
                    user = request.user,
                    content=content

                )
                
                messages.success(request,'Comment created.')
                return redirect('/')
            except new_comment.DoesNotExist:
                new_comment.delete()
                messages.error(request,"Something went wrong.")

    
# # fx to handle 404 error in the app
def page_not_found(request,exception):
    """
    Fx that handles Non-existent page Request.
    """

    template_name='404.html'
    status = 404

    # first render the 404 page
    return render(request,template_name,status=status)








        

        

