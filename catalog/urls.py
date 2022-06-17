from django.urls import path
# from django.urls import re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # Book
    path('books/', views.BookListView.as_view(), name='books'),
    path('books/print/', views.print_books_pdf, name='print_books'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
    path('books/update_summary', views.update_book_summary, name='update_book_summary'),

    # BookInstance
    path('bookinstances/', views.BookInstanceListView.as_view(), name='bookinstances'),
    path('bookinstance/<uuid:pk>/', views.BookInstanceDetailView.as_view(), name='bookinstance-detail'),
    path('bookinstance/create/', views.BookInstanceCreate.as_view(), name='bookinstance-create'),
    path('bookinstance/<uuid:pk>/update/', views.BookInstanceUpdate.as_view(), name='bookinstance-update'),
    path('bookinstance/<uuid:pk>/delete/', views.BookInstanceDelete.as_view(), name='bookinstance-delete'),

    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path('borrowed/', views.LoanedBooksListView.as_view(), name='all-borrowed'),

    # Authors
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),

    # Genres
    path('genres/', views.GenreList.as_view(), name='genres'),
    path('genre/<int:pk>/', views.GenreDetail.as_view(), name='genre-detail'),
    path('genre/create/', views.GenreCreate.as_view(), name='genre-create'),
    path('genre/<int:pk>/update/', views.GenreUpdate.as_view(), name='genre-update'),
    path('genre/<int:pk>/delete/', views.GenreDelete.as_view(), name='genre-delete'),

    # Language
    path('languages/', views.LanguageList.as_view(), name='languages'),
    path('language/<int:pk>/', views.LanguageDetail.as_view(), name='language-detail'),
    path('language/create/', views.LanguageCreate.as_view(), name='language-create'),
    path('language/<int:pk>/update/', views.LanguageUpdate.as_view(), name='language-update'),
    path('language/<int:pk>/delete/', views.LanguageDelete.as_view(), name='language-delete'),

    # Status
    path('statuses/', views.StatusList.as_view(), name='statuses'),
    path('status/<int:pk>/', views.StatusDetail.as_view(), name='status-detail'),
    path('status/create/', views.StatusCreate.as_view(), name='status-create'),
    path('status/<int:pk>/update/', views.StatusUpdate.as_view(), name='status-update'),
    path('status/<int:pk>/delete/', views.StatusDelete.as_view(), name='status-delete'),

    # Log
    path('logs/', views.LogList.as_view(), name='logs'),

    # re_path(r'^book/(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})',
    #         views.FilteredBookListView.as_view, name='filtered-book-detail'),
]
