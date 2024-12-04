from email import message
import re
from urllib import request
from django import template
from django.http import HttpResponseNotAllowed, QueryDict
from django.shortcuts import get_object_or_404, render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views import View


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

    
#today we setup loginpage and singup page.