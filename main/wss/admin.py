from django.contrib import admin
from .models import Sensor, HsvObject, Settings
from unfold.admin import ModelAdmin, forms

class HsvObjectAdminForm(forms.ModelForm):
    class Meta:
        model = HsvObject
        fields = '__all__'

    def clean_min_color_hsv(self):
        value = self.cleaned_data['min_color_hsv']
        if not isinstance(value, list) or len(value) != 3:
            raise forms.ValidationError("Введите список из трёх чисел [H, S, V]")
        return value

    def clean_max_color_hsv(self):
        value = self.cleaned_data['max_color_hsv']
        if not isinstance(value, list) or len(value) != 3:
            raise forms.ValidationError("Введите список из трёх чисел [H, S, V]")
        return value


@admin.register(HsvObject)
class HsvObjectAdmin(ModelAdmin):
    form = HsvObjectAdminForm
    list_display = ("name", "min_color_hsv", "max_color_hsv")
    search_fields = ("name",)
    fieldsets = (
        (None, {
            "fields": ("name",)
        }),
        ("HSV Диапазон", {
            "fields": ("min_color_hsv", "max_color_hsv")
        }),
    )


@admin.register(Sensor)
class SensorAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    fieldsets = (
        (None, {"fields": ("name",)}),
        ("Зоны интереса", {
            "fields": ("area_cord_one", "area_cord_two", "area_cord_check", "area_cordTwo_one", "area_cordTwo_two", "area_cordTwo_check")
        }),
    )

@admin.register(Settings)
class SettingsAdmin(ModelAdmin):
    list_display = ("sensor_center_one", "sensor_center_two")
    fieldsets = (
        ("Центральные датчики", {
            "fields": ("sensor_center_one", "sensor_center_two")
        }),
        ("Красные датчики", {
            "fields": ("sensor_red_front", "sensor_red_front_two", "sensor_red_left", "sensor_red_right")
        }),
        ("HSV Настройки", {
            "fields": (
                "hsv_red_one", "hsv_red_two",
                "hsv_blue", "hsv_green",
                "hsv_white", "hsv_black"
            )
        }),
    )

    def has_add_permission(self, request):
        return not Settings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
