from django.shortcuts import render,redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import json
from django.http import JsonResponse
import datetime
from django.db.models import Sum, Avg
# Create your views here.

def search_income(request):
    if request.method=='POST':
        search_str=json.loads(request.body).get('searchText')

        income=UserIncome.objects.filter(
            amount__istartswith=search_str,owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str,owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str,owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str,owner=request.user)
        
        data=income.values()

        return JsonResponse(list(data),safe=False)
    
@never_cache
@login_required(login_url='/authentication/login')
def index(request):
    categories=Source.objects.all()
    income=UserIncome.objects.filter(owner=request.user)
    paginator=Paginator(income,5)
    page_number=request.GET.get('page')
    page_obj=Paginator.get_page(paginator,page_number)
    currency=UserPreference.objects.get(user=request.user).currency
    context={
        'income':income,
        'page_obj':page_obj,
        'currency':currency,
    }
    return render(request, 'income/index.html',context) 

@never_cache
@login_required(login_url='/authentication/login') 
def add_income(request):
    sources = Source.objects.all()

    if request.method == 'GET':
        context = {
            'sources': sources,
        }
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('income_date')
        source = request.POST.get('source')

        context = {
            'sources': sources,
            'values': request.POST,
        }

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)

        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'income/add_income.html', context)

        if not source:
            messages.error(request, 'Source is required')
            return render(request, 'income/add_income.html', context)

        UserIncome.objects.create(
            owner=request.user,
            amount=amount,
            date=date,
            source=source,
            description=description
        )

        messages.success(request, 'Record saved successfully')
        return redirect('income')
    
@never_cache
@login_required(login_url='/authentication/login')
def income_edit(request, id):
    sources = Source.objects.all()
    income = UserIncome.objects.get(pk=id)

    if request.method == 'GET':
        context = {
            'income': income,
            'sources': sources
        }
        return render(request, 'income/edit_income.html', context)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('income_date')
        source = request.POST.get('source')

        context = {
            'income': income,
            'sources': sources,
            'values': request.POST
        }

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit_income.html', context)

        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'income/edit_income.html', context)

        if not source:
            messages.error(request, 'Source is required')
            return render(request, 'income/edit_income.html', context)

        income.amount = amount
        income.date = date
        income.source = source
        income.description = description
        income.save()

        messages.success(request, 'Record Updated successfully')
        return redirect('income')
    
def delete_income(request,id):
    income=UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request,'Record removed')
    return redirect('income')

def income_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    income = UserIncome.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)

    finalrep = {}

    def get_source(income):
        return income.source

    source_list = list(set(map(get_source, income)))

    def get_source_total(source):
        total = 0
        for item in income.filter(source=source):
            total += item.amount
        return total

    for x in source_list:
        finalrep[x] = get_source_total(x)

    return JsonResponse({'income_source_data': finalrep}, safe=False)

@never_cache
@login_required(login_url='/authentication/login')
def income_stats_view(request):
    user = request.user
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=30 * 6)

    income_records = UserIncome.objects.filter(owner=user)
    recent_income = income_records.order_by('-date')[:5]
    total_income = income_records.aggregate(total=Sum('amount'))['total'] or 0
    avg_income = income_records.aggregate(avg=Avg('amount'))['avg'] or 0
    top_source = income_records.values('source').annotate(total=Sum('amount')).order_by('-total').first()

    income_this_month = income_records.filter(date__year=today.year, date__month=today.month).aggregate(month_total=Sum('amount'))['month_total'] or 0

    context = {
        'total_income': round(total_income, 2),
        'average_income': round(avg_income, 2),
        'top_source': top_source['source'] if top_source else 'N/A',
        'income_this_month': round(income_this_month, 2),
        'recent_income': recent_income,
    }

    return render(request, 'income/stats.html', context)
