from django.db import models

from users.models import User


class Course(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название курса')
    description = models.TextField(verbose_name='Описание курса', null=True, blank=True)
    image = models.ImageField(upload_to='courses/', verbose_name='Изображение курса', null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    price = models.PositiveIntegerField(default=1000, verbose_name='Стоимость курса')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'


class Lesson(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название урока')
    description = models.TextField(verbose_name='Описание урока')
    image = models.ImageField(upload_to='courses/lessons/', verbose_name='Изображение урока', null=True, blank=True)
    link = models.URLField(verbose_name='Ссылка на видео', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.course} - {self.title}"

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_payments', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_payments')
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата платежа')
    payment_method = models.CharField(choices=[('1', 'Наличные'), ('2', 'Безнал')], verbose_name='Метод платежа')
    is_successful = models.BooleanField(default=False, verbose_name='Статус платежа')
    session = models.CharField(max_length=150, verbose_name='Сессия для оплаты', null=True, blank=True)

    def __str__(self):
        return f"{self.user}: {self.course} - {self.payment_date}"

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ('-payment_date',)


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_subscriptions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_subscriptions')

    def __str__(self):
        return f"{self.user}: {self.course}"

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
