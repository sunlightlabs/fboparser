from fbo_raw.models import Solicitation, Award, Justification, FairOpportunity
from django.shortcuts import render, redirect, get_object_or_404

def index(request):
    years = Justification.objects.dates('award_date', 'year')
    y = Justification.objects.all()
    return render(request, 'index.html', {'years': years, 'js' : y})
     
