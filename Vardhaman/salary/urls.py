from django.contrib import admin
from django.urls import path, include
from . import views
from .views import registerAPI, selectEmpData, calculateSalaryAPI, viewSalaryAPI, displayEmployee, deleteEmployee, advanceAPI, deleteAdvance,price_list


urlpatterns = [
    path('', views.home, name="add_employee"),
    path('registerAPI', registerAPI.as_view(), name="register_emp"),
    path('deleteEmployee', deleteEmployee.as_view(), name="deleteEmployee"),
    path('selectEmpDataAPI', selectEmpData.as_view(), name="get_emp_data"),
    path('calculateSalaryAPI', calculateSalaryAPI.as_view(), name="calculateSalaryAPI"),
    path('viewSalaryAPI', viewSalaryAPI.as_view(), name="calculateSalaryAPI"),
    path('displayEmployee', displayEmployee.as_view(), name="displayEmployee"),
    path('add_employee', views.add_employee, name="add_employee"),
    path('calculate_salary', views.calculate_salary, name="calculate_salary"),
    path('view_salary', views.view_salary, name="veiw_salary"),
    path('add_advance', views.add_advance, name="add_advance"),
    path('advanceAPI', advanceAPI.as_view(), name="advanceAPI"),
    path('deleteAdvance', deleteAdvance.as_view(), name="deleteAdvance"),
    path('price_list', price_list.as_view(), name="price_list"),


]