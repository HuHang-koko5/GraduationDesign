from django.db import models

# Create your models here.


class User(models.Model):
    '''用户表'''
    gender = (
        ('male', 'M'),
        ('female', 'F'),
    )

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    sex = models.CharField(max_length=32, choices=gender, default='M')
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

