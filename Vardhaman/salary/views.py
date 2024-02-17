import calendar
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from .serializers import *
from .models import *
from datetime import datetime, timedelta
from django.utils import timezone



def get_date_range(date_string):
    date_object = datetime.strptime(date_string, '%B %Y')
    # Extract the month and year
    selected_month = date_object.month  # Replace with the actual selected month
    selected_year = date_object.year  # Replace with the actual selected year
     # Generate the first day of the month
    first_day = datetime(selected_year, selected_month, 1)

    # Calculate the last day of the month
    _, last_day = calendar.monthrange(selected_year, selected_month)
    last_day = datetime(selected_year, selected_month, last_day)

    # Generate a range of dates for the selected month
    date_range = [first_day + timedelta(days=x) for x in range((last_day - first_day).days + 1)]
    return date_range

# Create your views here.
def home(request):
    return render(request,'base.html')

def add_employee(request):
    return render(request,'new_employee.html')

def calculate_salary(request):
    return render(request,'calc_salary.html')

def view_salary(request):
    return render(request,'view_salary.html')
class registerAPI(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        name = request.POST.get('name')
        salary_per_hour_str = request.POST.get('salary')
        salary_per_hour = int(salary_per_hour_str)
        print("-------------------------")
        print(name)
        print(salary_per_hour)
        print("-------------------------")
        existing_employee = EmployeeData.objects.filter(
            Q(name=name) 
        )
        print(existing_employee)
        print(existing_employee.exists())

        if existing_employee.exists():
            print("hello1")
            obj = existing_employee.first()
            obj.salary_per_hour = salary_per_hour
            obj.save()
        else:
            print("hello2")
            EmployeeData.objects.create(name=name, salary_per_hour=salary_per_hour)
        redirection_url = "/"
        response_data = {'redirection_url': redirection_url}
        return Response(response_data,status=status.HTTP_200_OK)
    
    def get(self,request):
        employees = EmployeeData.objects.all()
        
        # Serialize employee data
        employee_data = []
        for employee in employees:
            employee_data.append({
                'name': employee.name,
                'salary_per_hour': employee.salary_per_hour
            })
        print(employee_data)
        response_data = employee_data
        return Response(response_data,status=status.HTTP_200_OK)


class deleteEmployee(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        name = request.POST.get('name')
        print(name)
        EmployeeData.objects.filter(name=name).delete()
        redirection_url = "/"
        response_data = {'redirection_url': redirection_url}
        return Response(response_data,status=status.HTTP_200_OK)
    
class selectEmpData(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        print("here2")
        name = request.POST.get('emp_name')
        month_str = request.POST.get('month')
        print(name,month_str)
        date_range = get_date_range(month_str)
        dates_range =[]
        days_range =[]
        print("here3")

        date_object = datetime.strptime(month_str, '%B %Y')
        selected_month = date_object.month
        existing_work_schedules = WorkSchedule.objects.filter(emp_name__name=name, date__month=selected_month)
        start_times_hours = []
        start_times_minutes = []
        end_times_hours = []
        end_times_minutes = [] 
        lunch_times=[]       
        for date in date_range:
            schedule = existing_work_schedules.filter(date=date).first()
            if schedule:
                start_times_hours.append(schedule.start_time.hour)
                start_times_minutes.append(schedule.start_time.minute)
                end_times_hours.append(schedule.end_time.hour)
                end_times_minutes.append(schedule.end_time.minute)
                lunch_times.append(schedule.lunch_break)
            else:
                start_times_hours.append(None)
                start_times_minutes.append(None)
        
        print("here4")
        for date in date_range:
            dates_range += [date.strftime('%Y-%m-%d')]
            days_range += [date.strftime('%A')]
        # EmployeeData.objects.create(name=name)
        redirection_url = "/"
        response_data = {'redirection_url': redirection_url,'date_range':dates_range,'day_range':days_range,'start_times_hours': start_times_hours,'start_times_minutes': start_times_minutes,'end_times_hours': end_times_hours,'end_times_minutes': end_times_minutes,'lunch_break':lunch_times}
        return Response(response_data,status=status.HTTP_200_OK)

class displayEmployee(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        employee_list = EmployeeData.objects.values_list('name', flat=True)
        return JsonResponse({'names': list(employee_list)})
    
class calculateSalaryAPI(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        name = request.POST.get('emp_name')
        month_str = request.POST.get('month')
        # option_start = request.POST.get('options_start')
        # option_end = request.POST.get('options_end')
        formData = request.POST.dict()
        date_range = get_date_range(month_str)
        start_times = []
        end_times = []
        lunch_times = []
        dates_range =[]
        days_range =[]

        emp_name = EmployeeData.objects.get(name=name)

        date_object = datetime.strptime(month_str, '%B %Y')
        selected_month = date_object.month 

        existing_work_schedules = WorkSchedule.objects.filter(
            Q(emp_name=emp_name) &
            Q(date__month=selected_month)
        )

        # Delete existing WorkSchedule entries if they exist
        existing_work_schedules.delete()     

        print("here3")
        for date in date_range:
            dates_range += [date.strftime('%Y-%m-%d')]
            days_range += [date.strftime('%A')]

        print("here4")

        for key, value in formData.items():
            if key.startswith("start_"):
                index = key.split('_')[-1]
                start_hour_str = value
                if start_hour_str: 
                    start_hour = int(start_hour_str)
                    if formData.get(f"options_start_{index}") == 'Evening':
                        start_hour += 12
                else:
                    start_hour = None                          
                start_min = formData.get(f"starting_min_{index}")
                start_times.append(f"{start_hour}:{start_min}")

            elif key.startswith("end_"):
                index = key.split('_')[-1]
                end_hour_str = value
                if end_hour_str:  # Check if start_hour_str is not empty
                    end_hour = int(end_hour_str)
                    if formData.get(f"options_end_{index}") == 'Evening':
                        end_hour += 12
                else:
                    end_hour = None 
                end_min = formData.get(f"ending_min_{index}")
                end_times.append(f"{end_hour}:{end_min}")
            elif key.startswith("lunch_"):
                lunch_times.append(value)
        print("here5")

        a=0
        for i in start_times :
            if start_times[a] == 'None':
                print("-------------")
                start_times[a] = 0
            print("in for")
            
            a += 1
        a=0
        for i in end_times :
            if end_times[a] == 'None':
                end_times[a] = 0
            a += 1
        a=0
        for i in lunch_times :
            if lunch_times[a] == 'None':
                lunch_times[a] = 0                        
            a += 1
        print(start_times)
        print(end_times)
        print(lunch_times)
        # Get the Employee instance
        emp_name = EmployeeData.objects.get(name = name)
        a = 0
        for i in dates_range:
            if start_times[a] != "None:":
                print("Hello")
                work_schedule = WorkSchedule(
                        emp_name = emp_name,
                        date = dates_range[a],
                        start_time = datetime.strptime(start_times[a], '%H:%M').time(),
                        end_time = datetime.strptime(end_times[a], '%H:%M').time(),
                        lunch_break = lunch_times[a],
                )
                work_schedule.save()
            a += 1
        a = 0
        
        redirection_url = "/"
        response_data = {'redirection_url': redirection_url,'date_range':dates_range,'day_range':days_range}
        return Response(response_data,status=status.HTTP_200_OK)

class viewSalaryAPI(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        emp_name = request.GET.get('emp_name')
        month_year = request.GET.get('month')
        date_range = get_date_range(month_year)   
        dates_range =[]
        days_range =[]        
        for date in date_range:
            dates_range += [date.strftime('%Y-%m-%d')]
            days_range += [date.strftime('%A')]             
        print(emp_name)
        print(month_year)   

        try:
            split_values = month_year.rsplit(maxsplit=1)
            if len(split_values) != 2:
                raise ValueError("Invalid month and year format")

            month_name, year = split_values
            month = datetime.strptime(month_name, '%B').month
        except ValueError as e:
            print(f'Error parsing month and year: {e}')  # Add this line for debugging
            return Response({'error': 'Invalid month and year format'}, status=400)
     

        # Get all WorkSchedule entries for the given employee name and month
        work_schedules = WorkSchedule.objects.filter(
            emp_name__name=emp_name,
            date__month=month,
            date__year=year
        )

        time_per_day = []
        time_strings = []
        start_time = []
        end_time = []
        break_time = []
        total_time = timedelta()
        for work_schedule in work_schedules:
            start_datetime = datetime.combine(datetime.today(), work_schedule.start_time)
            end_datetime = datetime.combine(datetime.today(), work_schedule.end_time)            
            time_difference = end_datetime - start_datetime - timedelta(minutes=work_schedule.lunch_break)
            print(time_difference)
            total_time += time_difference
            time_per_day.append(time_difference)
            start_time.append(work_schedule.start_time)
            end_time.append(work_schedule.end_time)
            break_time.append(work_schedule.lunch_break)
            # time_per_day[a] = 

        print(total_time)
        print(time_per_day)
        for delta in time_per_day:
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            time_strings.append(f"{hours:02}:{minutes:02}")  # Format hours and minutes as HH:MM string

        print(time_strings)

        total_working_hours = int(total_time.total_seconds() // 3600)  # Convert to total hours
        remaining_seconds = total_time.total_seconds() % 3600
        total_working_minutes = int(remaining_seconds // 60) 
        total_time_worked = (f"{total_working_hours:02}:{total_working_minutes:02}")   
        print(total_time_worked)
        employee = EmployeeData.objects.get(name=emp_name)
        print(employee)
        salary_per_hour = employee.salary_per_hour
        total_salary = int((total_working_hours * salary_per_hour) + (total_working_minutes * (salary_per_hour/60)))
        print(total_salary)
            # print(work_schedule.end_time)
            # total_working_time += timedelta(work_schedule.end_time) - timedelta(work_schedule.start_time) - timedelta(minutes=work_schedule.lunch_break)
            # print(total_working_time)

            # total_working_hours = total_working_time.total_seconds() // 3600  # Convert to total hours
            # remaining_seconds = total_working_time.total_seconds() % 3600
            # total_working_minutes = remaining_seconds // 60  # Convert remaining seconds to total minutes
            # print(total_working_hours)
            # print(total_working_minutes)            


        # print(salary_per_hour)
        # print(total_working_hours)
        # print(total_working_minutes)


        # Serialize the result
        response_data = {'date_range':dates_range,'day_range':days_range,'start_time':start_time,'end_time':end_time,'break_time':break_time,'working_time_day': time_strings,'total_working_time': total_time_worked,'salary_per_hour': salary_per_hour,'total_salary': total_salary,}

        print(response_data)

        return Response(response_data)
