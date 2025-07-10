from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import *

def index(request):

  context = {
    'segment': 'dashboard',
  }
  return render(request, "dashboard/index.html", context)