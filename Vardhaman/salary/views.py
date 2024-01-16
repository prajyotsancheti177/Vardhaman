from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,'base.html')

def add_employee(request):
    return render(request,'base.html')

def calculate_salary(request):
    return render(request,'base.html')
