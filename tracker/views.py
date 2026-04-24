from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .models import Transaction, Category
from .forms import TransactionForm

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

@login_required
def add_transaction(request):
    if request.method == 'POST':
        # Получаем данные из POST-запроса
        transaction_type = request.POST.get('type')
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        description = request.POST.get('description')
        
        # Создаём транзакцию
        transaction = Transaction(
            user=request.user,
            type=transaction_type,
            category_id=category_id,
            amount=amount,
            date=date,
            description=description
        )
        transaction.save()
        return redirect('dashboard')
    else:
        # Разделяем категории на расходные и доходные
        expense_categories = Category.objects.filter(user=request.user, is_income=False)
        income_categories = Category.objects.filter(user=request.user, is_income=True)
        
        context = {
            'title': 'Добавить операцию',
            'expense_categories': expense_categories,
            'income_categories': income_categories,
        }
        
        # Если есть параметр type в GET (например, при редактировании), передаём его
        if 'type' in request.GET:
            context['selected_type'] = request.GET.get('type')
        
        return render(request, 'transaction_form.html', context)

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user)
    
    # Фильтрация
    transaction_type = request.GET.get('type')
    category_id = request.GET.get('category')
    
    if transaction_type:
        transactions = transactions.filter(type=transaction_type)
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    
    categories = Category.objects.filter(user=request.user)
    
    return render(request, 'transaction_list.html', {
        'transactions': transactions,
        'categories': categories,
        'current_type': transaction_type,
        'current_category': category_id,
    })

@login_required
def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Обновляем транзакцию
        transaction.type = request.POST.get('type')
        transaction.category_id = request.POST.get('category')
        transaction.amount = request.POST.get('amount')
        transaction.date = request.POST.get('date')
        transaction.description = request.POST.get('description')
        transaction.save()
        return redirect('transaction_list')
    else:
        # Разделяем категории
        expense_categories = Category.objects.filter(user=request.user, is_income=False)
        income_categories = Category.objects.filter(user=request.user, is_income=True)
        
        context = {
            'title': 'Редактировать операцию',
            'expense_categories': expense_categories,
            'income_categories': income_categories,
            'form': transaction,  # передаём транзакцию для отображения текущих значений
        }
        
        return render(request, 'transaction_form.html', context)

@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        return redirect('transaction_list')
    
    return render(request, 'transaction_confirm_delete.html', {'transaction': transaction})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Создаём стандартные категории для нового пользователя
            default_categories = [
                {'name': 'Еда', 'is_income': False},
                {'name': 'Транспорт', 'is_income': False},
                {'name': 'Кафе и рестораны', 'is_income': False},
                {'name': 'Супермаркеты', 'is_income': False},
                {'name': 'Связь и интернет', 'is_income': False},
                {'name': 'Зарплата', 'is_income': True},
                {'name': 'Подработка', 'is_income': True},
            ]
            
            for cat_data in default_categories:
                Category.objects.create(
                    user=user,
                    name=cat_data['name'],
                    is_income=cat_data['is_income'],
                    budget_limit=None  # можно потом установить
                )
            
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'category_list.html', {'categories': categories})

@login_required
def category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        is_income = request.POST.get('is_income') == 'on'
        budget_limit = request.POST.get('budget_limit') or None
        
        Category.objects.create(
            user=request.user,
            name=name,
            is_income=is_income,
            budget_limit=budget_limit
        )
        messages.success(request, f'Категория "{name}" создана!')
        return redirect('category_list')
    
    return render(request, 'category_form.html', {'title': 'Создать категорию'})

@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.is_income = request.POST.get('is_income') == 'on'
        category.budget_limit = request.POST.get('budget_limit') or None
        category.save()
        messages.success(request, f'Категория "{category.name}" обновлена!')
        return redirect('category_list')
    
    return render(request, 'category_form.html', {'category': category, 'title': 'Редактировать категорию'})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Категория "{category_name}" удалена!')
        return redirect('category_list')
    
    return render(request, 'category_confirm_delete.html', {'category': category})