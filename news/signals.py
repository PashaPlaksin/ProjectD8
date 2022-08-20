from django.db.models.signals import post_save
from django.dispatch import receiver # импортируем нужный декоратор

from .models import Post
from .tasks import new_post_subscription
# в декоратор передаётся первым аргументом сигнал, на который будет реагировать эта функция, и в отправители надо передать также модель
@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    new_post_subscription(instance)


