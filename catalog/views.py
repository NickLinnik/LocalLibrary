import os.path

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
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

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_books_with_crime_word': num_books_with_crime_word,
        'num_visits': num_visits,
    }

    return render(request, 'index.html', context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
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
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = os.path.join('catalog', 'bookinstance_list_borrowed_user.html')
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects\
            .filter(borrower=self.request.user)\
            .filter(status__exact='o')


class LoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    paginate_by = 10
    template_name = os.path.join('catalog', 'bookinstance_list_borrowed_all.html')

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o')
