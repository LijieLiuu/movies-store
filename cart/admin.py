from django.contrib import admin
from .models import Order, Item

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total", "date")
    list_filter = ("date", "user")
    search_fields = ("id", "user__username")

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "movie", "price", "quantity")
    list_filter = ("order", "movie")
    search_fields = ("id", "order__id", "movie__name")