import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import PROTECT
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
from django.utils.translation import gettext_lazy as _


class Genre(models.Model):
    """Model representing a book genre."""
    name = models.CharField(max_length=200, help_text='Enter the book genre (e.g. Science Fiction)')

    def __str__(self):
        """Return string for representing the genre."""
        return self.name

    def get_absolute_url(self):
        return reverse('genre-detail', args=[str(self.id)])


class Language(models.Model):
    name = models.CharField(max_length=200,
                            help_text="Enter the book's language (e.g. English, French, Japanese etc.)")

    def __str__(self):
        """String for representing the Language object (in Admin site etc.)"""
        return self.name

    def get_absolute_url(self):
        return reverse('language-detail', args=[str(self.id)])


class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=13, unique=True,
                            help_text='13 Character <a href=\
                            "https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')
    language_of_origin = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['title']

    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Genre'

    def __str__(self):
        """String for representing the book."""
        return self.title

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('book-detail', args=[str(self.id)])


class Status(models.Model):
    name = models.CharField(max_length=200, unique=True)
    extra_info = models.TextField(null=True, blank=True)

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('status-detail', args=[str(self.id)])

    def __str__(self): return self.name


class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text='Unique ID for this particular book across whole library')
    book = models.ForeignKey(Book, on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True, help_text='YYYY-MM-DD')
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """String for representing the particular instance of the book."""
        return f'{self.id} ({self.book.title})'

    def clean(self):
        if self.status in {0, 1} and (self.due_back or self.borrower):
            raise ValidationError(_('Invalid status - book can\'t have status '
                                    '"Available" or "Maintenance" while having Borrower and Renewal date'))

    @property
    def is_overdue(self):
        return bool(self.due_back and self.due_back < date.today())

    def get_absolute_url(self):
        return reverse('bookinstance-detail', args=[str(self.id)])

    def get_status(self):
        return self.status.name


class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True, help_text='YYYY-MM-DD')
    date_of_death = models.DateField('died', null=True, blank=True, help_text='YYYY-MM-DD')

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name}, {self.first_name}'


class Log(models.Model):
    model = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=PROTECT)
    date = models.DateTimeField()
    operation = models.CharField(max_length=50, null=True)

    def get_absolute_url(self):
        return reverse('log-detail', args=[str(self.id)])
