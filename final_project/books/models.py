from django.db import models

class Author(models.Model):
    idx = models.AutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=50)
    description = models.CharField(max_length=1000)

class Book(models.Model):
    idx = models.AutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=50)
    description = models.CharField(max_length=1000)
    author = models.ForeignKey(Author, related_name="books", on_delete=models.CASCADE)
    read_count = models.IntegerField(default=0)

class BookComment(models.Model):
    username = models.CharField(max_length=30)
    comment = models.CharField(max_length=1000)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)