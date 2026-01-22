from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from decouple import config
from .forms import Scamreportform
from .models import Scamreports, Scamtype
from .utils import ensure_google_social_app


def create_scam_types(request):
    types = [
        'Phishing', 'Impersonation', 
        'Investment Scam', 'Fake Job', 
        
        'Romance Scam', 'Giveaway Scam', 'Crypto Scam',
        'Tech Support Scam', 'Charity Scam', 
    ]
    for t in types:
        Scamtype.objects.get_or_create(name=t)
    return HttpResponse("✅ Scam types created.")

def report_scam(request):
    ensure_google_social_app()

    # ⬇️ Make sure scam_type choices are always correct
    scam_type_queryset = Scamtype.objects.all()

    if request.method == 'POST':
        form = Scamreportform(request.POST, request.FILES)
        form.fields['scam_type'].queryset = scam_type_queryset  # 🔥 force update

        if form.is_valid():
            scamreport = form.save(commit=False)
            if request.user.is_authenticated:
                scamreport.user = request.user

            scamreport.save()
            form.save_m2m()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok', 'message': 'Report submitted successfully'})

            return redirect('thank_you')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    else:
        form = Scamreportform()
        form.fields['scam_type'].queryset = scam_type_queryset  # 🔥 again for GET form

    return render(request, 'Scam_reports/report_scam.html', {'form': form})


def report_list(request):
    reports = Scamreports.objects.all()
    query = request.GET.get('q')
    if query:
        reports = reports.filter(
            Q(name_or_number__icontains=query) |
            Q(social_media__icontains=query)
        )

    filter_option = request.GET.get('filter', 'all')

    if filter_option == 'resolved':
        reports = reports.filter(is_resolved=True)
    elif filter_option == 'unresolved':
        reports = reports.filter(is_resolved=False)

    reports = reports.order_by('-date_reported')
    return render(request, 'Scam_reports/report_list.html', {'reports': reports, 'filter_option': filter_option})

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
            return redirect('user_dashboard')
    else:
        form = Scamreportform(instance=report)

    return render(request, 'edit_report.html', {'form': form})

def create_google_socialapp(request):
    ensure_google_social_app()

    site = Site.objects.get(id=1)

    app, created = SocialApp.objects.get_or_create(
        provider='google',
        name='Google',
        client_id=config('GOOGLE_CLIENT_ID'),
        secret=config('GOOGLE_CLIENT_SECRET')
    )
    app.sites.add(site)
    return HttpResponse("✅ Google SocialApp created.")


