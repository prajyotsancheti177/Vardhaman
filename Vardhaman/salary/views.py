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

def add_advance(request):
    return render(request,'add_advance.html') 

class advanceAPI(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        name = request.POST.get('emp_name')
        advnace_amount = request.POST.get('advance_amount')
        advance_date = datetime.now()
        print(advnace_amount)
        existing_employee = EmployeeData.objects.filter(Q(name=name))
        existing_data = EmployeeAdvance.objects.filter(emp_name=existing_employee.first())

        if existing_data.exists():
            print("hello1")
            obj = EmployeeAdvance.objects.filter(emp_name=existing_employee.first()).first()
            obj.advance_amount = advnace_amount
            obj.save()
        else:
            EmployeeAdvance.objects.create(emp_name=existing_employee.first(), advance_amount=advnace_amount, date=advance_date)

        redirection_url = "/"
        response_data = {'redirection_url': redirection_url}
        return Response(response_data,status=status.HTTP_200_OK)

    def get(self,request):
        all_advance = EmployeeAdvance.objects.all()

        # Serialize employee data
        advance_data = []
        for advance in all_advance:
            employee_data = EmployeeData.objects.filter(Q(name=advance.emp_name)).values('name')  # Replace 'other_field_name' with actual field names
            employee_data_dict = list(employee_data)[0] if employee_data else {}  # Extract the first element from the queryset or return an empty dictionary
            advance_data.append({
                'name': employee_data_dict.get('name', ''),  # Access the 'name' field from the dictionary
                'date': advance.date,
                'advance_amount': advance.advance_amount
            })
        print(advance_data)
        response_data = advance_data
        return Response(response_data,status=status.HTTP_200_OK)

class deleteAdvance(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        name = request.POST.get('name')
        existing_employee = EmployeeData.objects.filter(Q(name=name)).first()       
        EmployeeAdvance.objects.filter(emp_name=existing_employee).delete()
        redirection_url = "/"
        response_data = {'redirection_url': redirection_url}
        return Response(response_data,status=status.HTTP_200_OK)

class registerAPI(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        name = request.POST.get('name')
        salary_per_hour_str = request.POST.get('salary')
        new_name = request.POST.get('new_name')
        salary_per_hour = float(salary_per_hour_str)
        existing_employee = EmployeeData.objects.filter(
            Q(name=name) 
        )

        if existing_employee.exists():
            obj = existing_employee.first()
            print(new_name)
            print(obj.name)
            obj.salary_per_hour = salary_per_hour
            obj.name = new_name
            obj.save()
        else:
            # print("hello2")
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
        # print(employee_data)
        response_data = employee_data
        return Response(response_data,status=status.HTTP_200_OK)


class deleteEmployee(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        name = request.POST.get('name')
        # print(name)
        EmployeeData.objects.filter(name=name).delete()
        redirection_url = "/"
        response_data = {'redirection_url': redirection_url}
        return Response(response_data,status=status.HTTP_200_OK)
    
class selectEmpData(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        # print("here2")
        name = request.POST.get('emp_name')
        month_str = request.POST.get('month')
        # print(name,month_str)
        date_range = get_date_range(month_str)
        dates_range =[]
        days_range =[]
        # print("here3")

        date_object = datetime.strptime(month_str, '%B %Y')
        selected_month = date_object.month
        existing_work_schedules = WorkSchedule.objects.filter(emp_name__name=name, date__month=selected_month)
        start_times_hours = []
        start_times_minutes = []
        end_times_hours = []
        end_times_minutes = [] 
        lunch_times=[]    
        advance_salary = 0   

        existing_employee = EmployeeData.objects.filter(Q(name=name)).first()
        existing_advance = EmployeeAdvance.objects.filter(Q(emp_name=existing_employee) &Q(date=month_str))

        if(existing_advance.exists()):
            advance_salary = existing_advance.first().advance_amount
        else:
            advance_salary = 0

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
                end_times_hours.append(None)
                end_times_minutes.append(None)   
                lunch_times.append(None)             
        
        # print("here4")
        for date in date_range:
            dates_range += [date.strftime('%Y-%m-%d')]
            days_range += [date.strftime('%A')]
        # EmployeeData.objects.create(name=name)
        redirection_url = "/"
        response_data = {'redirection_url': redirection_url,'date_range':dates_range,'day_range':days_range,'start_times_hours': start_times_hours,'start_times_minutes': start_times_minutes,'end_times_hours': end_times_hours,'end_times_minutes': end_times_minutes,'lunch_break':lunch_times,'advance_salary':advance_salary}
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
        advance_amount = request.POST.get('advance_amount')

        emp_name = EmployeeData.objects.get(name=name)

        date_object = datetime.strptime(month_str, '%B %Y')
        selected_month = date_object.month 

        existing_work_schedules = WorkSchedule.objects.filter(
            Q(emp_name=emp_name) &
            Q(date__month=selected_month)
        )

        existing_advance = EmployeeAdvance.objects.filter(Q(emp_name=emp_name) &Q(date=month_str))

        if(existing_advance.exists()):
            # print("advance",advance_amount)
            existing_advance.update(advance_amount=advance_amount)
        else:
            EmployeeAdvance.objects.create(emp_name=emp_name, advance_amount=advance_amount, date=month_str)

        # Delete existing WorkSchedule entries if they exist
        existing_work_schedules.delete()     

        # print("here3")
        for date in date_range:
            dates_range += [date.strftime('%Y-%m-%d')]
            days_range += [date.strftime('%A')]

        # print("here4")

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
        # print("here5")

        a=0
        for i in start_times :
            if start_times[a] == 'None':
                # print("-------------")
                start_times[a] = 0            
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
        print(len(start_times))
        print(len(end_times))
        print(len(lunch_times))        
        # Get the Employee instance
        emp_name = EmployeeData.objects.get(name = name)
        a = 0
        for i in dates_range:
            if start_times[a] != "None:":
                # print("Hello")
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
        # print(emp_name)
        # print(month_year)
        advance_amount = 0
        
        existing_employee = EmployeeData.objects.filter(Q(name=emp_name)).first()
        existing_advance = EmployeeAdvance.objects.filter(Q(emp_name=existing_employee) &Q(date=month_year)).first()
        if(existing_advance):
            advance_amount = existing_advance.advance_amount
        else:
            advance_amount = 0

        try:
            split_values = month_year.rsplit(maxsplit=1)
            if len(split_values) != 2:
                raise ValueError("Invalid month and year format")

            month_name, year = split_values
            month = datetime.strptime(month_name, '%B').month
        except ValueError as e:
            # print(f'Error parsing month and year: {e}')  # Add this line for debugging
            return Response({'error': 'Invalid month and year format'}, status=400)
     

        # Get all WorkSchedule entries for the given employee name and month
        work_schedules = WorkSchedule.objects.filter(
            emp_name__name=emp_name,
            date__month=month,
            date__year=year
        )
        total_time = timedelta()
        time_per_day = []
        time_strings = []
        start_time = []
        end_time = []
        break_time = []
        for work_schedule in work_schedules:
            start_datetime = datetime.combine(datetime.today(), work_schedule.start_time)
            end_datetime = datetime.combine(datetime.today(), work_schedule.end_time)            
            time_difference = end_datetime - start_datetime - timedelta(minutes=work_schedule.lunch_break)
            # print(time_difference)
            print("total_time",total_time)
            print("Time Diffrence",time_difference)
            total_time += time_difference
            time_per_day.append(time_difference)
            start_time.append(work_schedule.start_time.strftime("%H:%M"))
            end_time.append(work_schedule.end_time.strftime("%H:%M"))
            break_time.append(work_schedule.lunch_break)
            # time_per_day[a] = 

        # print(total_time)
        # print(time_per_day)
        for delta in time_per_day:
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            time_strings.append(f"{hours:02}:{minutes:02}")  # Format hours and minutes as HH:MM string

        # print(time_strings)
        print(total_time)
        total_working_hours = int(total_time.total_seconds() // 3600)  # Convert to total hours
        remaining_seconds = total_time.total_seconds() % 3600
        total_working_minutes = int(remaining_seconds // 60) 
        total_time_worked = (f"{total_working_hours:02}:{total_working_minutes:02}")   
        # print(total_time_worked)
        employee = EmployeeData.objects.get(name=emp_name)
        # print(employee)
        salary_per_hour = employee.salary_per_hour
        total_salary = round(float((total_working_hours * salary_per_hour) + (total_working_minutes * (salary_per_hour/60))), 2)
        # print(total_salary)
        total_salary_after_advance = round(total_salary - advance_amount,2)
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
        response_data = {'date_range':dates_range,'day_range':days_range,'start_time':start_time,'end_time':end_time,'break_time':break_time,'working_time_day': time_strings,'total_working_time': total_time_worked,'salary_per_hour': salary_per_hour,'total_salary': total_salary,'advance_amount':advance_amount,'total_salary_after_advance':total_salary_after_advance}

        # print(response_data)

        return Response(response_data)


class price_list(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        all_products = PriceCalculation.objects.all()

        # Serialize employee data
        product_data = []
        for product in all_products:
            product_data.append({
                'product_name': product.product_name,
                'product_price': product.product_price
            })
        # print(employee_data)
        response_data = product_data
        return Response(response_data,status=status.HTTP_200_OK)

    def post(self, request):
        # Get the JSON data from the request body
        try:
            json_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data provided.'}, status=400)

        # Basic validation: Ensure JSON data is a list
        if not isinstance(json_data, list):
            return JsonResponse({'error': 'JSON data should be a list of objects.'}, status=400)

        try:
            for item in json_data:
                product_name = item.get('product_name')
                product_price = item.get('product_price')

                # Basic validation: Ensure product_name and product_price are provided
                if not product_name or not product_price:
                    return JsonResponse({'error': 'Both product_name and product_price are required.'}, status=400)

                # Attempt to update the product price
                existing_product = PriceCalculation.objects.filter(Q(product_name=product_name))
                if existing_product.exists():
                    existing_product.update(product_price=product_price)
                else:
                    # Handle case when product is not found
                    return JsonResponse({'error': f'Product "{product_name}" not found.'}, status=404)

            return JsonResponse({'success': 'Product prices updated successfully.'})
        except Exception as e:
            # Handle any errors that might occur during the update process
            return JsonResponse({'error': f'Error updating product prices: {str(e)}'}, status=500)        