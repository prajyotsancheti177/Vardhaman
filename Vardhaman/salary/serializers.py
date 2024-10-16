from rest_framework import serializers

class TotalWorkingTimeSerializer(serializers.Serializer):
    total_working_hours = serializers.IntegerField()
    total_working_minutes = serializers.IntegerField()
    total_salary = serializers.IntegerField()
