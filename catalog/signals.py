from django.db.models.signals import post_migrate, post_save, post_delete
from django.dispatch import receiver
from .apps import CatalogConfig
from .models import Author, Language, Book, BookInstance, Genre
from django.contrib.auth.models import User, Group


@receiver(post_migrate, sender=CatalogConfig, dispatch_uid='post_migrate_CatalogConfig')
@receiver(post_save, sender=Author, dispatch_uid='post_save_Author')
@receiver(post_save, sender=Book, dispatch_uid='post_save_Book')
def save_log(sender, **kwargs):
    print(sender)
