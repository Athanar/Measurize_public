import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Permission, User

datetime.datetime.now(tz=timezone.utc)

class DBUserinfo(models.Model):
    user_link = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    last_updated = models.DateField(default=datetime.date.today)

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    category_name = models.CharField(max_length=200)
    color = models.CharField(max_length=40, default="grey")
    def __str__(self):
        return self.category_name

class Measure(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    user_link = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    measure_name = models.CharField(max_length=200)
    measure_val = models.FloatField(default=0)
    measure_input = models.FloatField(default=0)
    result_number = models.FloatField(default=0)
    input_type = models.CharField(max_length=50, default="number")
    def __str__(self):
        return self.measure_name

class AmountModel(models.Model):
    measurefield_id = models.IntegerField(default=0)
    input_value = models.FloatField(default=0)
    input_amount = models.FloatField(default=0)
    creation_date = models.DateField(default=datetime.date.today)
    def __float__(self):
        return self.input_value

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    goal_value = models.FloatField(default=0)
    rate_of_change = models.FloatField(default=0)
    creation_date = models.DateField(default=datetime.date.today)