from django.shortcuts import render

from .models import Book, Author
from .forms import CommentForm
from .models import BookComment
from django.shortcuts import redirect

def author(request, id):
    author = Author.objects.get(idx=id)
    return render(request, 'author.html', context={"author": author})

def book(request, id):
    book = Book.objects.get(idx=id)
    comment_form = CommentForm()
    comments = BookComment.objects.filter(book=book)
    return render(request, 'book.html', context={"book": book, "comment_form": comment_form, "comments": comments})

def searchBook(request):
    if request.method == "POST":
        bookName = request.POST.get("bookName")
        books = Book.objects.filter(name__contains=bookName)
        return render(request, 'searchBook.html', context={"searchText": bookName, "books": books})

def sendComment(request):
    if request.method == "POST":
        username = request.POST.get("username")
        comment = request.POST.get("comment")
        book_id = int(request.POST.get("book_id"))
        book = Book.objects.get(idx=book_id)
        book_comment = BookComment(username=username, comment=comment, book=book)
        book_comment.save()
        return redirect("book", book_id)