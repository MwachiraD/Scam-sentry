from django.http import HttpResponseForbidden
from django.shortcuts import render , redirect ,get_object_or_404
from.forms import Scamreportform
from .models import Scamreports
from django.contrib import messages 
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import Scamreportform  
from django.http import JsonResponse
from django.http import HttpResponse
from .models import ScamType

form = Scamreportform(...)  





def create_scam_types(request):
    types = [
        'Phishing', 'Impersonation', 'Fake Marketplace',
        'Investment Scam', 'Fake Job', 'Online Dating Scam',
        'M-Pesa Fraud', 'Social Media Scam', 'Advance Fee Scam',
        'Romance Scam', 'Giveaway Scam', 'Crypto Scam',
        'Tech Support Scam', 'Charity Scam', 'Fake Purchase Scam'
    ]
    for t in types:
        ScamType.objects.get_or_create(name=t)
    return HttpResponse("✅ Scam types created.")

def report_scam(request):
    if request.method == 'POST':
        form = Scamreportform(request.POST, request.FILES)
        if form.is_valid():
            scamreport = form.save(commit=False)
            if request.user.is_authenticated:
                scamreport.user = request.user
            else:
                scamreport.is_whistleblower = True  # Handle anonymous users

            scamreport.save()
            form.save_m2m()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok', 'message': 'Report submitted successfully'})

            return redirect('thank_you')  # fallback for non-JS users

        else:
            # Form is invalid
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    # GET request or non-POST fallback
    form = Scamreportform()
    return render(request, 'Scam_reports/report_scam.html', {'form': form})


def report_list(request):
    reports=Scamreports.objects.all().order_by ('-date_reported')
    query = request.GET.get('q') 
    if query:
        reports = Scamreports.objects.filter(
            name_or_number__icontains=query
        ) | Scamreports.objects.filter(
            social_media__icontains=query
        )
    else:
        reports = Scamreports.objects.all()

    filter_option = request.GET.get('filter', 'all')

    if filter_option == 'resolved':
        reports = Scamreports.objects.filter(is_resolved=True)
    elif filter_option == 'unresolved':
        reports = Scamreports.objects.filter(is_resolved=False)
    else:
        reports = Scamreports.objects.all()

    return render(request, 'Scam_reports/report_list.html', {'reports': reports , 'filter_option': filter_option})

def thank_you(request):
     return render (request , "thank_you.html")

def mark_resolved(request, report_id):
    report = get_object_or_404(Scamreports, id=report_id)
    if request.user == report.user or request.user.is_staff:
        report.is_resolved = True
        report.save()
        messages.success(request, "Report marked as resolved.")
        return redirect('report_list')
    else:
        return HttpResponseForbidden("You don’t have permission to do that.")
    
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('report_scam')  # or dashboard later
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def user_dashboard(request):
    user_reports = Scamreports.objects.filter(user=request.user)
    return render(request, 'Scam_reports/dashboard.html', {'reports': user_reports})

@login_required
def edit_report(request, pk):
    report = get_object_or_404(Scamreports, pk=pk, user=request.user)

    if request.method == 'POST':
        form = Scamreportform(request.POST, instance=report)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = Scamreportform(instance=report)

    return render(request, 'edit_report.html', {'form': form})




