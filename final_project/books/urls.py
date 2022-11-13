from django.urls import path
from . import views

urlpatterns = [
    path("author/<int:id>", views.author, name="author"),
    path("book/<int:id>", views.book, name="book"),
    path("searchBook", views.searchBook, name="searchBook"),
    path("sendComment", views.sendComment, name="sendComment"),
]