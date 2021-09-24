from django.shortcuts import render
from django.views import generic
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


class BookListView(generic.ListView):
    model = Book
    paginate_by = 15
    context_object_name = 'book_list'  # default name
    # queryset = Book.objects.filter(title__icontains='crime')[:5]
    template_name = 'catalog/book_list_.html'  # Specify your own template name/location

    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='crime')[:5]

    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        context['list_end'] = 'This is the end of the list'
        return context


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 15


class AuthorDetailView(generic.DetailView):
    model = Author
