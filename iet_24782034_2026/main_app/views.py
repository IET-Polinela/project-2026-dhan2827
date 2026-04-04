from django.shortcuts import render, redirect
from .models import Report
from .forms import ReportForm

def home(request):
    return render(request, 'main_app/index.html')

def report_list(request):
    reports = Report.objects.all()
    return render(request, 'main_app/report_list.html', {'reports': reports})

def add_report(request):
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('report_list')
    else:
        form = ReportForm()

    return render(request, 'main_app/add_report.html', {'form': form})