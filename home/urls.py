from django.urls import path

from . import views

urlpatterns = [
    path('driverhome', views.driver_home, name='home'),
    path('industryhome', views.industry_home, name='home'),
    path('moddriverdetails', views.modify_driver_info, name="modify"),
    path('delete_account', views.delete_account, name="delete_acc"),
    path('sign_out', views.sign_out, name="signing_out")
]
