import datetime
import os.path

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import RenewBookForm, UpdateBookInstanceModelForm
from .models import Author, Book, BookInstance, Genre, Language


# http://localhost:8000/catalog/books/title/like/cr
class BooksByTitleLikeListView(generic.ListView):
    def get_queryset(self):
        return Book.objects.filter(title__icontains=self.kwargs['title'])

# http://localhost:8000/catalog/authors/born/between/1500-01-01/1900-01-01
class AuthorsBornBetweenListView(generic.ListView):
    def get_queryset(self):
        return Author.objects.filter(date_of_birth__range=
                                     [self.kwargs['date1'], self.kwargs['date2']])


def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.all().filter(status__exact='a').count()
    num_authors = Author.objects.all().count()
    num_genres = Genre.objects.all().count()
    num_books_with_crime_word = Book.objects.all().filter(title__contains='Crime').count()

    authors_with_max_books_map = {'first_name': 'first', 'last_name': 'last', 'count': 'count'}
    authors_with_max_books = Author.objects.raw('''
SELECT ca.id, ca.first_name, ca.last_name, COUNT(cb.id)
FROM catalog_author ca
         INNER JOIN catalog_book cb ON ca.id = cb.author_id
GROUP BY ca.id
HAVING COUNT(cb.id) >= ALL (SELECT COUNT(*)
                            FROM catalog_book ca
                            GROUP BY ca.author_id)''',
                                                translations=authors_with_max_books_map)

    # youngest_and_oldest_authors_map = {'first_name': 'first_name', 'last_name': 'last_name',
    #                                    'date_of_birth': 'date_of_birth',
    #                                    'date_of_death': 'date_of_death', 'comment': 'comment'}
    youngest_and_oldest_authors = Author.objects.raw('''
SELECT *, 'Oldest author(s) in the library' AS comment
FROM catalog_author
WHERE date_of_birth = (SELECT MIN(date_of_birth) FROM catalog_author)
UNION ALL
SELECT *, 'Youngest author(s) in the library' AS comment
FROM catalog_author
WHERE date_of_birth >= ALL (SELECT MAX(date_of_birth) FROM catalog_author)''')

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_books_with_crime_word': num_books_with_crime_word,
        'authors_with_max_books': authors_with_max_books,
        'youngest_and_oldest_authors': youngest_and_oldest_authors,

        'num_visits': num_visits,
    }

    return render(request, 'index.html', context)


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    # If this is a POST request then process the Form data
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # Create a form instance and populate it with data from the request (binding):
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
    # context = Language.objects.all()
    context_object_name = 'book_list'  # default name
    # queryset = Book.objects.filter(title__icontains='crime')[:5]
    template_name = 'catalog/book_list.html'  # Specify your own template name/location

    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='crime')[:5]

    # def get_queryset(self):
    #     return

    # def get_context_data(self, **kwargs):
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     context['list_end'] = 'This is the end of the list'
    #     return context


class BookDetailView(generic.DetailView):

    # log = Genre.objects.create(user=self.request.user,
    #       action_take='your description', row=something)
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author


class BookInstanceListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    paginate_by = 10


class BookInstanceDetailView(LoginRequiredMixin, generic.DetailView):
    model = BookInstance


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = os.path.join('catalog', 'bookinstance_list_borrowed_user.html')
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects \
            .filter(borrower=self.request.user) \
            .filter(status__exact='o')


class LoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    paginate_by = 10
    template_name = os.path.join('catalog', 'bookinstance_list_borrowed_all.html')

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o')


class GenreList(generic.ListView):
    model = Genre
    paginate_by = 10


class GenreDetail(generic.DetailView):
    model = Genre


class LanguageList(generic.ListView):
    model = Language
    paginate_by = 10


class LanguageDetail(generic.DetailView):
    model = Language


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    # initial = {'date_of_death': '11/06/2020'}


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('authors')


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language_of_origin']


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('books')


class BookInstanceCreate(PermissionRequiredMixin, CreateView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    fields = ['book', 'language', 'imprint', 'status']
    initial = {'status': 'a'}


class BookInstanceUpdate(PermissionRequiredMixin, UpdateView):
    form_class = UpdateBookInstanceModelForm
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'


class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'

    def get_success_url(self):
        return reverse_lazy('bookinstances')


class GenreCreate(PermissionRequiredMixin, CreateView):
    model = Genre
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class GenreUpdate(PermissionRequiredMixin, UpdateView):
    model = Genre
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class GenreDelete(PermissionRequiredMixin, DeleteView):
    model = Genre
    permission_required = 'catalog.can_mark_returned'

    def get_success_url(self):
        return reverse_lazy('genres')


class LanguageCreate(PermissionRequiredMixin, CreateView):
    model = Language
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class LanguageUpdate(PermissionRequiredMixin, UpdateView):
    model = Language
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class LanguageDelete(PermissionRequiredMixin, DeleteView):
    model = Language
    permission_required = 'catalog.can_mark_returned'

    def get_success_url(self):
        return reverse_lazy('languages')
