from django.contrib import admin

from .models import Customer, Order, Settings, Stop, Tour, Vehicle


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "city", "region", "phone", "is_active"]
    list_filter = ["region", "is_active"]
    search_fields = ["code", "name", "city"]


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ["registration_number", "type", "max_load_kg", "pallet_spaces", "is_active"]
    list_filter = ["type", "is_active"]
    search_fields = ["registration_number"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["number", "customer", "received_date", "dispatch_deadline", "weight_kg", "pallets", "status"]
    list_filter = ["status", "customer__region"]
    search_fields = ["number", "customer__name"]
    date_hierarchy = "dispatch_deadline"


# Postanki se urejajo kar na strani ture
class StopInline(admin.TabularInline):
    model = Stop
    extra = 0
    fields = ["sequence", "order", "driver_note", "result", "reason", "marked_at"]


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ["dispatch_date", "vehicle", "driver", "status", "created_by"]
    list_filter = ["status", "dispatch_date"]
    search_fields = ["vehicle__registration_number", "driver__last_name"]
    inlines = [StopInline]


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ["warehouse_address"]

    # Nastavitve imajo samo eno vrstico, zato nove ni mogoče dodati
    def has_add_permission(self, request):
        return not Settings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
