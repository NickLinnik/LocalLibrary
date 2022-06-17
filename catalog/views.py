import datetime
from os.path import join
import re
import pandas as pd
import pdfkit as pdf

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User

from .forms import RenewBookForm, UpdateBookInstanceModelForm
from .models import Author, Book, BookInstance, Genre, Language, Log, Status

config = pdf.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
html_dir = join('catalog', 'static', 'prints', 'html')
pdf_dir = join('catalog', 'static', 'prints', 'pdf')


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

    def get_queryset(self):
        return Book.objects.filter(title__icontains=self.request.GET.get('like', ''))


def print_books_pdf(request):
    df = pd.DataFrame(Book.objects.values(
        'title', 'author__first_name', 'author__last_name', 'summary', 'isbn', 'language_of_origin__name')) \
        .rename(columns={'title': 'Title', 'author__first_name': 'Author first name', 'summary': 'Summary',
                         'author__last_name': 'Author last name', 'language_of_origin__name': 'Language'})
    # print(df)
    df.to_html(join(html_dir, 'book_list.html'))
    line = '''<h1>LocalLibrary booklist</h1>'''
    with open(join(html_dir, 'book_list.html'), 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)
    pdf.from_file(join(html_dir, 'book_list.html'), join(pdf_dir, 'book_list.pdf'), configuration=config)
    return redirect('index')


class BookDetailView(generic.DetailView):
    # log = Genre.objects.create(user=self.request.user,
    #       action_take='your description', row=something)
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 20

    def get_queryset(self):
        date1 = self.request.GET.get('date1')
        date2 = self.request.GET.get('date2')
        return (Author.objects.filter(date_of_birth__range=[date1, date2]) if date1 and date2 else
                Author.objects.filter(date_of_birth__gte=date1) if date1 else
                Author.objects.filter(date_of_death__lte=date2) if date2 else
                Author.objects.all())


class AuthorDetailView(generic.DetailView):
    model = Author


class BookInstanceListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    paginate_by = 20


class BookInstanceDetailView(LoginRequiredMixin, generic.DetailView):
    model = BookInstance


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = join('catalog', 'bookinstance_list_borrowed_user.html')
    paginate_by = 20

    def get_queryset(self):
        return BookInstance.objects \
            .filter(borrower=self.request.user) \
            .filter(status__exact=3)


class LoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    paginate_by = 20
    template_name = join('catalog', 'bookinstance_list_borrowed_all.html')

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact=3)


class GenreList(generic.ListView):
    model = Genre
    paginate_by = 20


class GenreDetail(generic.DetailView):
    model = Genre


class LanguageList(generic.ListView):
    model = Language
    paginate_by = 20


class LanguageDetail(generic.DetailView):
    model = Language


class StatusList(generic.ListView):
    model = Status
    paginate_by = 20


class StatusDetail(generic.DetailView):
    model = Status


class CRUD_DispatcherView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            Log(model=self.model.__name__, user_id=request.user.id, date=datetime.datetime.now(),
                operation=re.search(r'Create|Update|Delete', str(super()))[0]).save()
        return self.post(request, *args, **kwargs)


class AuthorCreate(CRUD_DispatcherView, PermissionRequiredMixin, CreateView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorUpdate(CRUD_DispatcherView, PermissionRequiredMixin, UpdateView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('authors')

    def post(self, request, *args, **kwargs):
        Log(model=self.model.__name__, user_id=request.user.id, date=datetime.datetime.now(),
            operation=re.search(r'Create|Update|Delete', str(super()))[0]).save()
        return super().post(self, request, *args, **kwargs)


class BookCreate(CRUD_DispatcherView, PermissionRequiredMixin, CreateView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language_of_origin']


class BookUpdate(CRUD_DispatcherView, PermissionRequiredMixin, UpdateView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('books')

    def post(self, request, *args, **kwargs):
        Log(model=self.model.__name__, user_id=request.user.id, date=datetime.datetime.now(),
            operation=re.search(r'Create|Update|Delete', str(super()))[0]).save()
        return super().post(self, request, *args, **kwargs)


class BookInstanceCreate(CRUD_DispatcherView, PermissionRequiredMixin, CreateView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    fields = ['book', 'language', 'imprint', 'status']
    initial = {'status': 1}


class BookInstanceUpdate(CRUD_DispatcherView, PermissionRequiredMixin, UpdateView):
    form_class = UpdateBookInstanceModelForm
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'


class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'

    def get_success_url(self):
        return reverse_lazy('bookinstances')

    def post(self, request, *args, **kwargs):
        Log(model=self.model.__name__, user_id=request.user.id, date=datetime.datetime.now(),
            operation=re.search(r'Create|Update|Delete', str(super()))[0]).save()
        return super().post(self, request, *args, **kwargs)


class GenreCreate(CRUD_DispatcherView, PermissionRequiredMixin, CreateView):
    model = Genre
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class GenreUpdate(CRUD_DispatcherView, PermissionRequiredMixin, UpdateView):
    model = Genre
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class GenreDelete(PermissionRequiredMixin, DeleteView):
    model = Genre
    permission_required = 'catalog.can_mark_returned'

    def get_success_url(self):
        return reverse_lazy('genres')

    def post(self, request, *args, **kwargs):
        Log(model=self.model.__name__, user_id=request.user.id, date=datetime.datetime.now(),
            operation=re.search(r'Create|Update|Delete', str(super()))[0]).save()
        return super().post(self, request, *args, **kwargs)


class LanguageCreate(CRUD_DispatcherView, PermissionRequiredMixin, CreateView):
    model = Language
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class LanguageUpdate(CRUD_DispatcherView, PermissionRequiredMixin, UpdateView):
    model = Language
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class LanguageDelete(PermissionRequiredMixin, DeleteView):
    model = Language
    permission_required = 'catalog.can_mark_returned'

    def get_success_url(self):
        return reverse_lazy('languages')

    def post(self, request, *args, **kwargs):
        Log(model=self.model.__name__, user_id=request.user.id, date=datetime.datetime.now(),
            operation=re.search(r'Create|Update|Delete', str(super()))[0]).save()
        return super().post(self, request, *args, **kwargs)


class StatusCreate(CRUD_DispatcherView, PermissionRequiredMixin, CreateView):
    model = Status
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class StatusUpdate(CRUD_DispatcherView, PermissionRequiredMixin, UpdateView):
    model = Status
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class StatusDelete(PermissionRequiredMixin, DeleteView):
    model = Status
    permission_required = 'catalog.can_mark_returned'

    def get_success_url(self):
        return reverse_lazy('statuses')

    def post(self, request, *args, **kwargs):
        Log(model=self.model.__name__, user_id=request.user.id, date=datetime.datetime.now(),
            operation=re.search(r'Create|Update|Delete', str(super()))[0]).save()
        return super().post(self, request, *args, **kwargs)


class LogList(generic.ListView):
    model = Log
    paginate_by = 10


def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.all().filter(status__exact=0).count()
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

    user_loaned_books_count = User.objects.raw('''SELECT au.id, username, COUNT(cbi.id)
FROM auth_user au
         INNER JOIN catalog_bookinstance cbi ON au.id = cbi.borrower_id
GROUP BY au.id;''')

    author_biggest_bookinstance_count = Author.objects.raw('''SELECT ca.id, first_name, last_name, title
FROM catalog_author ca
         INNER JOIN catalog_book cb ON ca.id = cb.author_id
WHERE cb.id IN (SELECT cb1.id
                FROM catalog_bookinstance cbi
                         INNER JOIN catalog_book cb1 ON cb1.id = cbi.book_id
                WHERE author_id = ca.id
                GROUP BY cb1.id
                HAVING COUNT(cbi.id) >= ALL (SELECT COUNT(*)
                                             FROM catalog_bookinstance cbi1
                                                      INNER JOIN catalog_book cb1
                                                                 ON cb1.id = cbi1.book_id
                                             WHERE author_id = ca.id
                                             GROUP BY cb1.id));''')

    books_without_instances = Book.objects.raw('''SELECT cb.id, title
FROM catalog_book cb
         LEFT JOIN catalog_bookinstance cbi
             ON cb.id = cbi.book_id
WHERE cbi.id IS NULL;''')

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
        'user_loaned_books_count': user_loaned_books_count,
        'author_biggest_bookinstance_count': author_biggest_bookinstance_count,
        'books_without_instances': books_without_instances,

        'num_visits': num_visits,
    }

    return render(request, 'index.html', context)


@login_required
def update_book_summary(request):
    with connection.cursor() as cursor:
        cursor.execute('''UPDATE catalog_book
SET summary = CONCAT(summary, ' Highest number of genres in library.')
WHERE (summary NOT LIKE '%. Highest number of genres in library.%')
  AND id IN (SELECT book_id
             FROM catalog_book_genre
             GROUP BY book_id
             HAVING COUNT(genre_id) >= ALL (SELECT COUNT(genre_id)
                                            FROM catalog_book_genre
                                            GROUP BY book_id));''')
    return redirect('index')


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
