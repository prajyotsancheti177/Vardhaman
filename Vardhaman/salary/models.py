from django.db import models
import uuid

# Create your models here.
class EmployeeData(models.Model):
    name = models.CharField(max_length=255, unique=True)
    salary_per_hour = models.FloatField(default=0)
    def __str__(self):
        return self.name
    
class WorkSchedule(models.Model):
    emp_name = models.ForeignKey(EmployeeData, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    lunch_break = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.emp_name} - {self.start_time} to {self.end_time}"
    
    class Meta:
        # Define composite primary key using unique_together
        unique_together = ('emp_name', 'date') 

class EmployeeAdvance(models.Model):
    emp_name = models.ForeignKey(EmployeeData, on_delete=models.CASCADE)
    date = models.CharField(max_length=255)
    advance_amount = models.FloatField(default=0)

class PriceCalculation(models.Model):
    product_name = models.CharField(max_length=255)
    product_price = models.FloatField(default=0)
