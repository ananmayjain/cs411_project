from django.urls import path

from . import views

urlpatterns = [
    path('driverhome', views.driver_home, name='home'),
    path('industryhome', views.industry_home, name='home'),
    path('moddriverdetails', views.modify_driver_info, name="modify_driver"),
    path('modindustrydetails', views.modify_industry_info, name="modify_industry"),
    path('delete_account', views.delete_account, name="delete_acc"),
    path('sign_out', views.sign_out, name="signing_out"),
    path('find_drivers', views.find_drivers, name="find_drivers"),
    path('find_driver_past_rides', views.find_driver_past_rides, name="find_driver_past_rides")
]
