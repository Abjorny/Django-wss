from django.db import models
from django.core.exceptions import ValidationError

class HsvObject(models.Model):
    name = models.CharField(max_length=100, verbose_name="Заголовок для админ панели")
    min_color_hsv = models.JSONField("Минимальный (HSV)", default=list)
    max_color_hsv = models.JSONField("Максимальный (HSV)", default=list)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Объект HSV"
        verbose_name_plural = "Объекты HSV"

class Sensor(models.Model):
    name = models.CharField(max_length=100, verbose_name="Заголовок для админ панели")

    area_cord_one = models.JSONField("Зона интереса для первого этажа", null = True, blank = True)
    area_cord_two = models.JSONField("Зона интереса для второго этажа", null = True, blank = True)

    area_cordTwo_one = models.JSONField("Зона интереса для первого этажа, когда робот на втором", null = True, blank = True)
    area_cordTwo_two = models.JSONField("Зона интереса для второго этажа, когда робот на втором", null = True, blank = True)
    
    area_cord_check = models.JSONField("Зона интереса для проверки второго этажа", null = True, blank = True)
    area_cordTwo_check = models.JSONField("Зона интереса для проверки второго этажа, когда робот на втором", null = True, blank = True)



    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Датчик"
        verbose_name_plural = "Датчики"


class Settings(models.Model):
    sensor_center_one = models.ForeignKey(Sensor, on_delete=models.CASCADE, verbose_name="Первый датчик по центру", related_name='center_one')
    sensor_center_two = models.ForeignKey(Sensor, on_delete=models.CASCADE, verbose_name="Второй датчик по центру", related_name='center_two')
    sensor_left = models.ForeignKey(Sensor, on_delete=models.CASCADE, verbose_name="Левый датчик по центру", related_name='center_left', null=True, blank=True)
    sensor_right = models.ForeignKey(Sensor, on_delete=models.CASCADE, verbose_name="Правый датчик по центру", related_name='center_right', null=True, blank=True)

    sensor_red_front = models.ForeignKey(Sensor, on_delete=models.CASCADE, verbose_name="Первый красный датчик спереди", related_name='red_front', null = True, blank = True)
    sensor_red_front_two = models.ForeignKey(Sensor, on_delete=models.CASCADE, verbose_name="Второй красный датчик спереди", related_name='red_front_two', null = True, blank = True)
    sensor_red_left = models.ForeignKey(Sensor, on_delete=models.CASCADE, verbose_name="Красный датчик слева", related_name='red_left', null = True, blank = True)
    sensor_red_right = models.ForeignKey(Sensor, on_delete=models.CASCADE, verbose_name="Красный датчик српава", related_name='red_right', null = True, blank = True)

    hsv_red_one = models.ForeignKey(HsvObject, on_delete=models.CASCADE, verbose_name="HSV красного первый", related_name='hsv_red_one')
    hsv_red_two = models.ForeignKey(HsvObject, on_delete=models.CASCADE, verbose_name="HSV красного второй", related_name='hsv_red_two')

    hsv_blue = models.ForeignKey(HsvObject, on_delete=models.CASCADE, verbose_name="HSV синего", related_name='hsv_blue')
    hsv_green = models.ForeignKey(HsvObject, on_delete=models.CASCADE, verbose_name="HSV зеленного", related_name='hsv_green')

    hsv_white = models.ForeignKey(HsvObject, on_delete=models.CASCADE, verbose_name="HSV белого", related_name='hsv_white')
    hsv_black = models.ForeignKey(HsvObject, on_delete=models.CASCADE, verbose_name="HSV черного", related_name='hsv_black')

    def clean(self):
        if not self.pk and Settings.objects.exists():
            raise ValidationError("Нельзя создать более одного объекта настроек!")

    def __str__(self):
        return "Настройки"

    class Meta:
        verbose_name = "Настройки"
        verbose_name_plural = "Настройки"
