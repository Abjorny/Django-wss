from django.contrib import admin
from .models import  HsvObject, Settings, Mission, Action
from adminsortable2.admin import SortableInlineAdminMixin
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

class ActionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Action
    extra = 1
    fields = ('time', 'compos')

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    inlines = [ActionInline]


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


@admin.register(Settings)
class SettingsAdmin(ModelAdmin):
    fieldsets = (
        ("HSV Настройки", {
            "fields": (
                "hsv_red_one", "hsv_red_two",
            )
        }),
    )

    def has_add_permission(self, request):
        return not Settings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
