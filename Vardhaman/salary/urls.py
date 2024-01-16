from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="add_employee"),
    path('add_employee', views.add_employee, name="add_employee"),
    path('calculate_salary', views.calculate_salary, name="calculate_salary"),
]