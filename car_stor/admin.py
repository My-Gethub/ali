from django.contrib import admin
from .models import Car, Category, BlogPost, Accessory, ContactMessage, CarOrder, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['accessory']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'email', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    inlines = [OrderItemInline]

@admin.register(CarOrder)
class CarOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'car', 'full_name', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'old_price', 'status', 'seller', 'created_at')
    list_filter = ('status', 'fuel_type', 'transmission', 'category')
    search_fields = ('title', 'description', 'engine')
    
    # Force simple text input for numbers to avoid browser validation issues
    from django.forms import TextInput
    from django.db import models
    formfield_overrides = {
        models.DecimalField: {'widget': TextInput},
        models.IntegerField: {'widget': TextInput},
    }

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'content')

@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'created_at')
    search_fields = ('title', 'description')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')

from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'phone')

