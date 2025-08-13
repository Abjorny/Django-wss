from django.db import models
from django.core.exceptions import ValidationError




class Mission(models.Model):
    name = models.CharField(max_length=100)
    speed = models.PositiveIntegerField("Скорость")
    def __str__(self):
        return self.name


class Action(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='actions')
    time = models.PositiveIntegerField("Время")
    compos = models.PositiveIntegerField("Компос")
    order = models.PositiveIntegerField(default=0)


    class Meta:
        ordering = ['order'] 

    def __str__(self):
        return f"{self.mission.name} — {self.compos} ({self.time}s)"

class HsvObject(models.Model):
    name = models.CharField(max_length=100, verbose_name="Заголовок для админ панели")
    min_color_hsv = models.JSONField("Минимальный (HSV)", default=list)
    max_color_hsv = models.JSONField("Максимальный (HSV)", default=list)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Объект HSV"
        verbose_name_plural = "Объекты HSV"



class Settings(models.Model):
    hsv_red_one = models.ForeignKey(HsvObject, on_delete=models.CASCADE, verbose_name="HSV красного первый", related_name='hsv_red_one')
    hsv_red_two = models.ForeignKey(HsvObject, on_delete=models.CASCADE, verbose_name="HSV красного второй", related_name='hsv_red_two')
    
    hsv_black = models.ForeignKey(HsvObject, on_delete=models.CASCADE, verbose_name="HSV черного", related_name='hsv_black')
    hsv_white = models.ForeignKey(HsvObject, on_delete=models.CASCADE, verbose_name="HSV белого", related_name='hsv_white')
    
    
    first_mission = models.ForeignKey(Mission, on_delete=models.CASCADE, verbose_name="Первая миссия", related_name='first_mission', null = True, blank= True)

    def clean(self):
        if not self.pk and Settings.objects.exists():
            raise ValidationError("Нельзя создать более одного объекта настроек!")

    def __str__(self):
        return "Настройки"

    class Meta:
        verbose_name = "Настройки"
        verbose_name_plural = "Настройки"
