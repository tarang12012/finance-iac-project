from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from userpreferences.models import UserPreference
from django.db.models.functions import TruncMonth
from django.db.models import Sum,Max
import datetime
# Create your views here.

def search_expenses(request):
    if request.method=='POST':
        search_str=json.loads(request.body).get('searchText')

        expenses=Expense.objects.filter(
            amount__istartswith=search_str,owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str,owner=request.user) | Expense.objects.filter(
            description__icontains=search_str,owner=request.user) | Expense.objects.filter(
            category__icontains=search_str,owner=request.user)
        
        data=expenses.values()

        return JsonResponse(list(data),safe=False)

@never_cache
@login_required(login_url='/authentication/login')
def index(request):
    categories=Category.objects.all()
    expenses=Expense.objects.filter(owner=request.user)
    paginator=Paginator(expenses,2)
    page_number=request.GET.get('page')
    page_obj=Paginator.get_page(paginator,page_number)
    preference, created = UserPreference.objects.get_or_create(user=request.user)
    currency = preference.currency if preference.currency else 'INR'
    context={
        'expenses':expenses,
        'page_obj':page_obj,
        'currency':currency,
    }
    return render(request, 'expenses/index.html',context) 

@never_cache
@login_required(login_url='/authentication/login') 
def add_expense(request):
    categories=Category.objects.all()
    context={
            'categories':categories,
            'values':request.POST,
        }
    if request.method=='GET':
        return render(request, 'expenses/add_expense.html', context) 

    if request.method=='POST':
        amount=request.POST['amount']

        if not amount:
            messages.error(request,'Amount is required')
            return render(request, 'expenses/add_expense.html', context) 
        
        description=request.POST['description']
        date=request.POST['expense_date']
        category=request.POST['category']

        if not description:
            messages.error(request,'Description is required')
            return render(request, 'expenses/add_expense.html', context)
        
        Expense.objects.create(owner=request.user,amount=amount,date=date,category=category,description=description)
        messages.success(request,'Expense saved successfully')

        return redirect('expenses')
    
@never_cache
@login_required(login_url='/authentication/login')   
def expense_edit(request,id):
    categories=Category.objects.all()
    expense=Expense.objects.get(pk=id)
    context={
        'expense':expense,
        'values':expense,
        'categories':categories
    }
    if request.method=='GET':
        return render(request,'expenses/edit-expense.html',context)
    if request.method=='POST':
        amount=request.POST['amount']

        if not amount:
            messages.error(request,'Amount is required')
            return render(request, 'expenses/edit_expense.html', context) 
        
        description=request.POST['description']
        date=request.POST['expense_date']
        category=request.POST['category']

        if not description:
            messages.error(request,'Description is required')
            return render(request, 'expenses/edit_expense.html', context)
        expense.owner=request.user
        expense.amount=amount
        expense.date=date
        expense.category=category
        expense.description=description

        expense.save()
        messages.success(request,'Expense Updated successfully')
            

        return redirect('expenses')
    
@never_cache
@login_required(login_url='/authentication/login')
def delete_expense(request,id):
    expense=Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request,'Expense removed')
    return redirect('expenses')

@never_cache
@login_required(login_url='/authentication/login')
def expense_category_summary(request):
    todays_date=datetime.date.today()
    six_months_ago=todays_date-datetime.timedelta(days=30*6)
    expenses=Expense.objects.filter(owner=request.user,date__gte=six_months_ago,date__lte=todays_date)
    finalrep={}

    def  get_category(expense):
        return expense.category
    
    category_list=list(set(map(get_category,expenses)))

    def get_expense_category_amount(category):
        amount=0
        filtered_by_category=expenses.filter(category=category)

        for item in filtered_by_category:
            amount+=item.amount

        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y]=get_expense_category_amount(y)

    return JsonResponse({'expense_category_data':finalrep},safe=False)

@never_cache
@login_required(login_url='/authentication/login')
def stats_view(request):
    user = request.user
    today = datetime.date.today()
    six_months_ago = today - datetime.timedelta(days=30 * 6)

    expenses = Expense.objects.filter(owner=user)
    total_spent = expenses.aggregate(total=Sum('amount'))['total'] or 0

    monthly_data = expenses.filter(date__gte=six_months_ago, date__lte=today) \
        .annotate(month=TruncMonth('date')) \
        .values('month') \
        .annotate(total=Sum('amount')) \
        .order_by('month')

    labels = [entry['month'].strftime('%b %Y') for entry in monthly_data]
    totals = [float(entry['total']) for entry in monthly_data]
    avg_monthly_spend = round(sum(totals) / len(totals), 2) if totals else 0


    category_data = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
    top_category = category_data[0] if category_data else {'category': None, 'total': 0}

    
    recent_expenses = expenses.order_by('-date')[:5]

    context = {
        'total_spent': total_spent,
        'avg_monthly_spend': avg_monthly_spend,
        'labels': json.dumps(labels),
        'totals': json.dumps(totals),
        'top_category': top_category,
        'recent_expenses': recent_expenses,
    }
    return render(request, 'expenses/stats.html', context)



@never_cache
@login_required(login_url='/authentication/login')
def monthly_expense_trend(request):
    today = datetime.date.today()
    six_months_ago = today - datetime.timedelta(days=30 * 6)

    expenses = Expense.objects.filter(
        owner=request.user,
        date__gte=six_months_ago,
        date__lte=today
    ).annotate(month=TruncMonth('date')) \
     .values('month') \
     .annotate(total=Sum('amount')) \
     .order_by('month')

    labels = [expense['month'].strftime("%b %Y") for expense in expenses]
    data = [float(expense['total']) for expense in expenses]

    return JsonResponse({
        'labels': labels,
        'data': data
    })