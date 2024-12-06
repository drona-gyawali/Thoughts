"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app.models import *
from app.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user-site/', ContentView.as_view(),name = 'user-site'),
    path('user-site/update/<int:id>/', Update_View.as_view(),name='update'),
    path('user-site/delete/<int:id>/', delete_page,name ='delete'),
    path('login-page/', Loginpage.as_view(),name='login-page'),
    path('sign-up/',SignUp.as_view(), name = 'sign-up'),
    path('logout/',log_out,name='logout'),
    path('forget-password/',forget_password.as_view(),name ='forget-password'),
    path('verify-otp/',Otpverfication.as_view(), name = 'verify-otp'),
    path('reset-password/<username>/',ResetPassword.as_view(),name ='reset-password')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns+= staticfiles_urlpatterns()