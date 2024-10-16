from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.calculator, name="calculator"),
    path('manage-products/', views.manage_products, name='manage_products'),
    path('save-screenshot/', views.save_screenshot, name='save_screenshot'),
]