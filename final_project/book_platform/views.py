from django.shortcuts import render

from books.models import Book

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def categories(request):
    most_read_books = Book.objects.order_by("-read_count")[0:3]
    return render(request, 'categories.html', context={"most_read_books": most_read_books})

def contact(request):
    return render(request, 'contact.html')