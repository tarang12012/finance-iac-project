from django.urls import path
from . import views

#app_name = 'userpreferences'

urlpatterns = [
    path('',views.index,name="preferences")
]