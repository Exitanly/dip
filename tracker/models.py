from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """Категория расходов/доходов (например: Еда, Транспорт, Зарплата)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100, verbose_name='Название')
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Лимит на месяц')
    is_income = models.BooleanField(default=False, verbose_name='Категория дохода')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Transaction(models.Model):
    """Финансовая операция (расход или доход)"""
    TYPE_CHOICES = [
        ('expense', 'Расход'),
        ('income', 'Доход'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    date = models.DateField(auto_now_add=False, verbose_name='Дата')
    description = models.CharField(max_length=255, blank=True, verbose_name='Описание')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='expense', verbose_name='Тип')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    def __str__(self):
        return f"{self.get_type_display()}: {self.amount} - {self.category}"
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'