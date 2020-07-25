from django.urls import path

from . import views

urlpatterns = [
    path('driverhome', views.driver_home, name='home'),
    path('industryhome', views.industry_home, name='home'),
    path('moddriverdetails', views.modify_driver_info, name="modify")
]
