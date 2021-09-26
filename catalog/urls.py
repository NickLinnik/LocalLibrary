from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('authors/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path('borrowed/', views.LoanedBooksListView.as_view(), name='all-borrowed')
    # re_path(r'^book/(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})',
    #         views.FilteredBookListView.as_view, name='filtered-book-detail'),
]
