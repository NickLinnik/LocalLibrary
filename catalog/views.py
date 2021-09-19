from django.shortcuts import render
from .models import Author, Book, BookInstance, Genre

def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.all().filter(status__exact='a').count()
    num_authors = Author.objects.all().count()
    num_genres = Genre.objects.all().count()
    num_books_with_crime_word = Book.objects.all().filter(title__contains='Crime').count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_books_with_crime_word': num_books_with_crime_word,
    }

    return render(request, 'index.html', context)
