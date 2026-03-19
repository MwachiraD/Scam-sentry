import traceback
from io import StringIO

from django.contrib import messages
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from datetime import timedelta
from difflib import get_close_matches
from django.core.management import call_command
from django.core.cache import cache
from django.db.models import Q, F
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from decouple import config
from .forms import (
    Scamreportform,
    ReportAbuseForm,
    ReportFollowForm,
    ReportCommentForm,
    WatchlistForm,
    DigestSubscriptionForm,
)
from .models import (
    Scamreports,
    Scamtype,
    ReportAbuse,
    ReportFollow,
    ReportComment,
    ReportEditLog,
    WatchlistItem,
    DigestSubscription,
)
from .services import send_weekly_digest
from .utils import ensure_google_social_app


def create_scam_types(request):
    types = [
        'Phishing',
        'Impersonation',
        'Investment Scam',
        'Fake Job',
        'Romance Scam',
        'Giveaway Scam',
        'Crypto Scam',
        'Tech Support Scam',
        'Charity Scam',
        'Purchase Scam',
        'Marketplace Scam',
        'Lottery Scam',
        'Loan Scam',
        'Account Takeover',
        'Delivery Scam',
        'Rental Scam',
        'WhatsApp Scam',
        'M-Pesa Fraud',
    ]
    for t in types:
        Scamtype.objects.get_or_create(name=t)
    return HttpResponse("Scam types created.")

def _get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')

def _rate_limited(request, key, limit, window_seconds):
    ip = _get_client_ip(request)
    if not ip:
        return False
    cache_key = f"rl:{key}:{ip}"
    current = cache.get(cache_key)
    if current is None:
        cache.set(cache_key, 1, window_seconds)
        return False
    if current >= limit:
        return True
    cache.incr(cache_key)
    return False

def report_scam(request):
    # Make sure scam_type choices are always correct
    scam_type_queryset = Scamtype.objects.all()

    if request.method == 'POST':
        if _rate_limited(request, 'report_submit', limit=5, window_seconds=600):
            message = "Too many submissions. Please wait a bit and try again."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': message}, status=429)
            form = Scamreportform()
            form.fields['scam_type'].queryset = scam_type_queryset
            return render(request, 'Scam_reports/report_scam.html', {'form': form, 'error_message': message})
        form = Scamreportform(request.POST, request.FILES)
        form.fields['scam_type'].queryset = scam_type_queryset

        if form.is_valid():
            scamreport = form.save(commit=False)
            if request.user.is_authenticated:
                scamreport.user = request.user
            scamreport.is_hidden = True

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
        form.fields['scam_type'].queryset = scam_type_queryset

    summary = cache.get('report_summary')
    if summary is None:
        visible_reports = Scamreports.objects.filter(is_hidden=False)
        total_reports = visible_reports.count()
        trending_count = visible_reports.filter(date_reported__gte=timezone.now() - timedelta(days=7)).count()
        last_report = visible_reports.order_by('-date_reported').first()
        summary = {
            'total_reports': total_reports,
            'trending_count': trending_count,
            'last_reported': last_report.date_reported if last_report else None,
        }
        cache.set('report_summary', summary, 300)

    return render(request, 'Scam_reports/report_scam.html', {'form': form, 'summary': summary})


def report_list(request):
    reports = Scamreports.objects.all().prefetch_related('scam_type')
    if not request.user.is_staff:
        reports = reports.filter(is_hidden=False)
    query = request.GET.get('q')
    if query and _rate_limited(request, 'search', limit=30, window_seconds=60):
        return HttpResponse("Too many searches. Please wait a minute and try again.", status=429)
    if query:
        reports = reports.filter(
            Q(name_or_number__icontains=query) |
            Q(social_media__icontains=query)
        )
    if query and not reports.exists():
        reports = Scamreports.objects.filter(is_hidden=False).filter(
            Q(name_or_number__icontains=query) |
            Q(social_media__icontains=query) |
            Q(scam_type__name__icontains=query)
        ).distinct()

    filter_option = request.GET.get('filter', 'all')

    if filter_option == 'resolved':
        reports = reports.filter(is_resolved=True)
    elif filter_option == 'unresolved':
        reports = reports.filter(is_resolved=False)

    selected_types = request.GET.getlist('type')
    if selected_types:
        reports = reports.filter(scam_type__id__in=selected_types).distinct()

    date_filter = request.GET.get('date', 'all')
    if date_filter == '7d':
        reports = reports.filter(date_reported__gte=timezone.now() - timedelta(days=7))
    elif date_filter == '30d':
        reports = reports.filter(date_reported__gte=timezone.now() - timedelta(days=30))

    reports = reports.order_by('-date_reported')
    scam_types = cache.get('scam_types_list')
    if scam_types is None:
        scam_types = list(Scamtype.objects.all())
        cache.set('scam_types_list', scam_types, 600)

    suggestion = None
    if query and not reports.exists():
        candidates = [t.name for t in scam_types]
        matches = get_close_matches(query, candidates, n=1, cutoff=0.6)
        suggestion = matches[0] if matches else None

    trending_reports = cache.get('trending_reports')
    if trending_reports is None:
        trending_cutoff = timezone.now() - timedelta(days=7)
        trending_reports = list(
            Scamreports.objects.filter(date_reported__gte=trending_cutoff, is_hidden=False)
            .order_by('-encounter_count', '-date_reported')[:6]
        )
        cache.set('trending_reports', trending_reports, 300)

    context = {
        'reports': reports,
        'filter_option': filter_option,
        'scam_types': scam_types,
        'selected_types': selected_types,
        'date_filter': date_filter,
        'query': query,
        'suggestion': suggestion,
        'trending_reports': trending_reports,
        'digest_form': DigestSubscriptionForm(),
    }
    return render(request, 'Scam_reports/report_list.html', context)


def encounter_report(request, report_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    report = get_object_or_404(Scamreports, id=report_id)
    if report.is_hidden and not request.user.is_staff:
        return HttpResponseForbidden("This report is not available.")
    encountered = request.session.get('encountered_reports', [])
    if report_id not in encountered:
        Scamreports.objects.filter(id=report_id).update(encounter_count=F('encounter_count') + 1)
        report.refresh_from_db(fields=['encounter_count'])
        encountered.append(report_id)
        request.session['encountered_reports'] = encountered

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'encounter_count': report.encounter_count})

    return redirect('report_list')


def report_abuse(request, report_id):
    report = get_object_or_404(Scamreports, id=report_id)
    if request.method == 'POST':
        form = ReportAbuseForm(request.POST)
        if form.is_valid():
            abuse = form.save(commit=False)
            abuse.report = report
            abuse.save()
            return render(request, 'Scam_reports/report_abuse_thanks.html', {'report': report})
    else:
        form = ReportAbuseForm()
    return render(request, 'Scam_reports/report_abuse.html', {'form': form, 'report': report})


def report_detail(request, report_id):
    report = get_object_or_404(Scamreports.objects.prefetch_related('scam_type'), id=report_id)
    if report.is_hidden and not request.user.is_staff:
        return HttpResponseForbidden("This report is not available.")
    follow_form = ReportFollowForm()
    comment_form = ReportCommentForm()
    watchlist_form = WatchlistForm()
    comments = report.comments.filter(is_approved=True).order_by('-created_at')
    return render(
        request,
        'Scam_reports/report_detail.html',
        {
            'report': report,
            'follow_form': follow_form,
            'comment_form': comment_form,
            'watchlist_form': watchlist_form,
            'comments': comments,
        },
    )


def follow_report(request, report_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    report = get_object_or_404(Scamreports, id=report_id)
    if report.is_hidden and not request.user.is_staff:
        return HttpResponseForbidden("This report is not available.")
    form = ReportFollowForm(request.POST)
    if form.is_valid():
        ReportFollow.objects.get_or_create(report=report, email=form.cleaned_data['email'])
        return render(request, 'Scam_reports/report_follow_thanks.html', {'report': report})
    comment_form = ReportCommentForm()
    watchlist_form = WatchlistForm()
    comments = report.comments.filter(is_approved=True).order_by('-created_at')
    return render(
        request,
        'Scam_reports/report_detail.html',
        {
            'report': report,
            'follow_form': form,
            'comment_form': comment_form,
            'watchlist_form': watchlist_form,
            'comments': comments,
        },
    )


def add_comment(request, report_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    report = get_object_or_404(Scamreports, id=report_id)
    if report.is_hidden and not request.user.is_staff:
        return HttpResponseForbidden("This report is not available.")
    form = ReportCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.report = report
        comment.save()
        return render(request, 'Scam_reports/report_comment_thanks.html', {'report': report})
    follow_form = ReportFollowForm()
    watchlist_form = WatchlistForm()
    comments = report.comments.filter(is_approved=True).order_by('-created_at')
    return render(
        request,
        'Scam_reports/report_detail.html',
        {
            'report': report,
            'follow_form': follow_form,
            'comment_form': form,
            'watchlist_form': watchlist_form,
            'comments': comments,
        },
    )


@login_required
def add_watchlist(request, report_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    report = get_object_or_404(Scamreports, id=report_id)
    WatchlistItem.objects.get_or_create(
        user=request.user,
        name_or_number=report.name_or_number,
        social_media=report.social_media or "",
    )
    return render(request, 'Scam_reports/watchlist_thanks.html', {'report': report})


@login_required
def watchlist(request):
    items = WatchlistItem.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'Scam_reports/watchlist.html', {'items': items})


def digest_subscribe(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    form = DigestSubscriptionForm(request.POST)
    if form.is_valid():
        subscription, _ = DigestSubscription.objects.get_or_create(email=form.cleaned_data['email'])
        if request.user.is_authenticated:
            subscription.user = request.user
            subscription.save(update_fields=['user'])
        return render(request, 'Scam_reports/digest_thanks.html', {})
    return redirect('report_list')


def cron_weekly_digest(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    expected_secret = config('CRON_SECRET', default='').strip()
    if not expected_secret and not settings.DEBUG:
        return JsonResponse({'status': 'error', 'message': 'CRON_SECRET is not configured.'}, status=500)

    if expected_secret:
        authorization = request.headers.get('Authorization', '')
        if authorization != f'Bearer {expected_secret}':
            return HttpResponseForbidden('Invalid cron authorization.')

    result = send_weekly_digest()
    status_code = 200 if result['status'] in {'sent', 'noop'} else 500
    return JsonResponse(result, status=status_code)


@csrf_exempt
def deploy_init(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    expected_secret = config('CRON_SECRET', default='').strip()
    if not expected_secret and not settings.DEBUG:
        return JsonResponse({'status': 'error', 'message': 'CRON_SECRET is not configured.'}, status=500)

    if expected_secret:
        authorization = request.headers.get('Authorization', '')
        if authorization != f'Bearer {expected_secret}':
            return HttpResponseForbidden('Invalid init authorization.')

    outputs = {}
    try:
        for command_name, command_kwargs in (
            ('migrate', {'interactive': False}),
            ('seed_scam_types', {}),
        ):
            stdout = StringIO()
            stderr = StringIO()
            call_command(command_name, stdout=stdout, stderr=stderr, **command_kwargs)
            outputs[command_name] = {
                'stdout': stdout.getvalue(),
                'stderr': stderr.getvalue(),
            }
    except Exception:
        return JsonResponse(
            {
                'status': 'error',
                'message': 'Database initialization failed.',
                'outputs': outputs,
                'traceback': traceback.format_exc(),
            },
            status=500,
        )

    return JsonResponse({'status': 'ok', 'message': 'Database initialized.', 'outputs': outputs})


@login_required
def moderation_queue(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to view this page.")
    pending_reports = Scamreports.objects.filter(is_hidden=True).order_by('-date_reported')[:50]
    open_abuse = ReportAbuse.objects.filter(status='open').order_by('-created_at')[:50]
    return render(request, 'Scam_reports/moderation_queue.html', {'pending_reports': pending_reports, 'open_abuse': open_abuse})


def policy(request):
    return render(request, 'Scam_reports/policy.html')


@login_required
def approve_report(request, report_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    if not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to do that.")
    report = get_object_or_404(Scamreports, id=report_id)
    report.is_hidden = False
    report.is_verified = True
    report.save(update_fields=['is_hidden', 'is_verified'])
    return redirect('moderation_queue')


@login_required
def reject_report(request, report_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    if not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to do that.")
    report = get_object_or_404(Scamreports, id=report_id)
    report.is_hidden = True
    report.is_verified = False
    report.save(update_fields=['is_hidden', 'is_verified'])
    return redirect('moderation_queue')

def thank_you(request):
     return render (request , "thank_you.html")

def mark_resolved(request, report_id):
    report = get_object_or_404(Scamreports, id=report_id)
    if request.user == report.user or request.user.is_staff:
        report.is_resolved = True
        report.resolution_reason = request.POST.get('resolution_reason', '')
        report.resolved_at = timezone.now()
        report.save()
        messages.success(request, "Report marked as resolved.")
        return redirect('report_list')
    else:
        return HttpResponseForbidden("You don't have permission to do that.")
    
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
            if form.has_changed():
                changes = {}
                for field in form.changed_data:
                    changes[field] = {
                        'from': getattr(report, field),
                        'to': form.cleaned_data.get(field),
                    }
                ReportEditLog.objects.create(report=report, user=request.user, changes=changes)
            form.save()
            return redirect('user_dashboard')
    else:
        form = Scamreportform(instance=report)

    return render(request, 'edit_report.html', {'form': form})

def create_google_socialapp(request):
    ensure_google_social_app()
    return HttpResponse('Google SocialApp synced.')


