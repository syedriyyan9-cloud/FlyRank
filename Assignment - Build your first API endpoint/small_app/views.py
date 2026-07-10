from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.

def home(request):
    '''send data to homepage'''
    data = {
        'f_name' : 'syed',
        'age' : 22,
        'is_internee': True,
        'intern_at' : 'FlyRank'
    }
    return JsonResponse(data)

def about(request):
    '''send data to about page'''
    data = {
        'm_name': 'riyyan',
        'program': 'backend AI',
        'lives_in': 'Lahore'
    }
    return JsonResponse(data)