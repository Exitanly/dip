from django.contrib import admin
from .models import Category, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'budget_limit', 'is_income']
    list_filter = ['user', 'is_income']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'category', 'date', 'type']
    list_filter = ['user', 'type', 'category', 'date']