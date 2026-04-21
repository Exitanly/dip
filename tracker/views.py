from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Transaction, Category

@login_required
def dashboard(request):
    user = request.user
    
    # Получаем все транзакции пользователя
    transactions = Transaction.objects.filter(user=user)
    
    # Считаем доходы и расходы
    total_income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense
    
    # Данные для графика: расходы по категориям
    expense_by_category = transactions.filter(type='expense').values('category__name').annotate(total=Sum('amount'))
    
    category_labels = [item['category__name'] for item in expense_by_category]
    category_data = [float(item['total']) for item in expense_by_category]
    
    # Последние 5 транзакций
    recent_transactions = transactions[:5]
    
    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'category_labels': category_labels,
        'category_data': category_data,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'dashboard.html', context)