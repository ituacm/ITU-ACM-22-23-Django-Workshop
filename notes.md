## Django'nun yüklenmesi ve projenin oluşturulması
`pipenv shell`

`pip install django`

`django-admin startproject book_platform`

Daha sonra dıştaki `book_platform` klasörünün adı karışıklık olmaması adına `book_platform_con` olarak değiştirilebilir.

## Projenin çalıştırılması
`pipenv shell` -> Zaten virtual env içinde bulunuluyorsa çalıştırılmasına gerek yok.

`cd book_platform_con`

`python manage.py runserver`

## URL routing
### urls.py
```
from . import views

path("", views.index, name="index")
```
### views.py
```
from django.shortcuts import render

def index(request):
    render(request, 'index.html')
```

## Frontend'in projeye dahil edilmesi
### settings.py
`TEMPLATES>"DIRS": ["templates"]`

```
STATICFILES_DIRS = [
    BASE_DIR / "statics",
]
```

### Dahil edilen sayfaların viewlerinin eklenmesi
`views.py` dosyası aşağıdaki gibi olmalıdır:

```
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def categories(request):
    return render(request, 'categories.html')

def contact(request):
    return render(request, 'contact.html')
```


Bütün kaynaklar (CSS, JS, resimler) static olarak yüklenmelidir. Örneğin aşağıdaki gibi bir değişiklik yapılmalıdır:

HTML dosyasının başına `{% load static %}` yazıldıktan sonra,

`<img src="images/slider-img.png" alt="">` -> `<img src="{% static 'images/slider-img.png' %}" alt="">`

Referans linkleri (href) için ise aşağıdaki gibi bir değişiklik yapılmalıdır:

`<a class="nav-link" href="about.html"> About</a>` -> `<a class="nav-link" href="{% url 'about' %}"> About</a>`

### Template Inheritance
`_base.html` her sayfanın bulunacağı yapıdadır. Diğer sayfalar bunu extend eder.

`_base.html`'de `{% block content %} {% endblock %}`

Diğer sayfalarda 
```
{% extends "_base.html" %}

{% block content %}

<Yalnızca o sayfaya ait içerik>

{% endblock %}
```

## Kitap listeleme
### Yeni app oluşturulması
Projenin organizasyonunun sağlanması için, proje çeşitli app'lere ayrılabilir. Örneğin, `books` ve `authors` modellerinin ve view'lerinin ayrı bir app'de tutulmasını isteyebiliriz. Aşağıdaki komutla yeni bir app oluşturulabilir:

`python manage.py startapp books`
#### Yeni app için URL routing
Ana `urls.py` dosyasında aşağıdaki değişiklik ile birlikte `books/` path'i `books` uygulamasına yönlendirilir:

```
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("categories/", views.categories, name="categories"),
    path("contact/", views.contact, name="contact"),
    path("books/", include("books.urls")),
]
```
`include` fonksiyonu bunu sağlamaktadır.

`books/urls.py` dosyası da aşağıdaki şekildedir:

```
from django.urls import path
from . import views

urlpatterns = [
    path("author/<int:id>", views.author, name="author"),
    path("book/<int:id>", views.book, name="book"),
    path("searchBook", views.searchBook, name="searchBook")
]
```

`<int:id>`, URL'nin içerisinde `int` türünde bir `id` parametresi de olduğunu belirtmektedir. View oluştururken parametre ismi buraya girilenle aynı olmak zorundadır. Örneğin:

```
def author(request, id):
    return render(request, 'author.html')
```


App oluşturulduktan sonra `book_platform/settings.py`'a aşağıdaki gibi eklenmelidir:

```
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "books.apps.BooksConfig",
]
```

### Kitap modelinin oluşturulması
#### books/models.py
```
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
```

Yukarıda, `AutoField`'in görevi, yeni bir kayıt eklendiğinde indeksin otomatik olarak artmasını sağlamaktır, böylece her kayda erişilebilir. `Primary key` olarak verilmesinin sebebi ise bir kayda erişeceğimiz zaman indeksini vererek erişebilmektir.

### Bir model oluşturulduktan sonra veritabanında kaydın oluşturulması
Model oluşturduktan sonra

```
python manage.py makemigrations

python manage.py migrate
```

komutları sırayla girilir. Bu komutlar, class olarak belirttiğimiz tabloların veritabanındaki karşılıklarının oluşturulmasını sağlamaktadır.

### Modelleri admin panelinde görme
Django bize default olarak bir admin panel sağlamaktadır. `url/admin` dizini ile birlikte bu panele erişebiliriz.

#### Admin kullanıcısı oluşturma
`python manage.py createsuperuser`

Kullanıcı adı ve şifre girildikten sonra admin kullanıcısı oluşturulacaktır.

#### Book ve Author modellerinin admin panelde gözükmesi
Modellerin admin panele register edilmesi için `books/admin.py` dosyası aşağıdaki şekilde olmalıdır:

```
from django.contrib import admin

from books.models import Book, Author

# Register your models here.
admin.site.register(Book)
admin.site.register(Author)
```

Bu işlemlerden sonra admin panelinden veritabanına yeni kayıtlar eklenebilir.

#### Kitap arama
`categories.html` dosyasında, arama kısmı aşağıdaki şekilde olmalıdır:

```
<form class="search_form" action="{% url 'searchBook' %}" method="POST">
  {% csrf_token %}
  <input type="text" name="bookName" class="form-control bg-light" placeholder="Search here...">
    <button class="bg-info" type="submit">
      <i class="fa fa-search" aria-hidden="true"></i>
    </button>
</form>
```

`<form>` tagında istek metodunun POST olduğu ve submit edince `searchBook` viewine yönlendirileceği belirtildi, `<input>` tagına parametre ismi `name="bookName"` şeklinde verildi, `{% csrf_token %}` ise templatelerde her formun altında güvenlik sağlamak için bulunmak zorundadır.

`books/views.py` dosyasındaki searchBook viewi aşağıdaki şekilde olmalıdır:

```
from .models import Book

def searchBook(request):
    if request.method == "POST":
        bookName = request.POST.get("bookName")
        books = Book.objects.filter(name__contains=bookName)
        return render(request, 'searchBook.html', context={"searchText": bookName, "books": books})
```

Burada, yukarıda `name="bookName"` ile belirttiğimiz parametrenin okunması, ardından veritabanında içerisinde aranan texti içeren kayıtların elde edilmesi, ardından gerekli bilgilerin `context` parametresiyle template'e verilmesi işlemleri yapıldı.

`searchBook.html` dosyası ise aşağıdaki gibi olmalıdır:

```
{% extends "_base.html" %}

{% load static %}

{% block content %}
<!-- catagory section -->
<section class="catagory_section layout_padding">
  <div class="catagory_container">
    <div class="container">
      <div class="heading_container heading_center">
        <h3 class="mb-3">
          Search results - {{ searchText }}
        </h3>
      </div>
      {% for book in books %}
      <div class="row">
        <div class="col-sm-12 col-md-12 mb-12">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">{{ book.name }}</h5>
              <p class="card-text">{{ book.description }}</p>
              <a href="{% url 'book' book.idx %} " class="btn btn-primary">Details</a>
            </div>
          </div>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
</section>

<!-- end catagory section -->
{% endblock %}
```

Burada view'da girilen arama texti (`searchText`) yazdırıldı ve her bir kitap bir for döngüsü ile yazdırıldı.

### En çok okunan kitapların listelenmesi

`categories.html` dosyası aşağıdaki şekilde olmalıdır:

```
{% extends "_base.html" %}

{% load static %}

<!-- catagory section -->
{% block content %}
<section class="catagory_section layout_padding">
  <div class="catagory_container">
    <div class="heading_container heading_center">
      <h2>
        Search Books
      </h2>
      <p>
        There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration
      </p>
    </div>
    <div class="container">
      <div class="container w-50 mb-5">
        <form class="search_form" action="{% url 'searchBook' %}" method="POST">
          {% csrf_token %}
          <input type="text" name="bookName" class="form-control bg-light" placeholder="Search here...">
          <button class="bg-info" type="submit">
            <i class="fa fa-search" aria-hidden="true"></i>
          </button>
        </form>
      </div>

      <div class="heading_container heading_center">
        <h3 class="mb-3">
          Most Read Books
        </h3>
      </div>
      {% for book in most_read_books %}
      <div class="row">
        <div class="col-sm-6 col-md-4 mb-3">
          <div class="card" style="width: 18rem;">
            <div class="card-body">
              <h5 class="card-title">{{ book.name }}</h5>
              <p class="card-text">{{ book.description }}</p>
              <a href="{% url 'book' book.idx %}" class="btn btn-primary">Details</a>
            </div>
          </div>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
  </div>
</section>
<!-- end catagory section -->
{% endblock %}
```

`book_platform/views.py` dosyasında ise `categories` viewi aşağıdaki şekilde olmalıdır:

```
from books.models import Book, Author

def categories(request):
    most_read_books = Book.objects.order_by("-read_count")[0:3]
    return render(request, 'categories.html', context={"most_read_books": most_read_books})
```

Burada kitaplar okunma sayısına göre azalan şekilde sıralanarak en çok okunan 3 kitap elde edilip template'e gönderilmiştir.

### Tekil kitap ve yazar sayfalarının oluşturulması
`books/views.py` dosyasındaki `book` view'i aşağıdaki şekilde düzenlenir:

```
def book(request, id):
    book = Book.objects.get(idx=id)
    return render(request, 'book.html', context={"book": book})
```

`book.html` ise aşağıdaki şekilde olmalıdır:

```
{% extends "_base.html" %}

{% block content %}
<section class="about_section layout_padding">
  <div class="container ">
    <div class="row">
      <div class="col-md-5">
      </div>
      <div class="col-md-5">
        <div class="detail-box">
          <div class="heading_container">
            <h2>
              {{ book.name }}
            </h2>
          </div>
          <p>
            {{ book.description }}
          </p>
        </div>
      </div>
    </div>
  </div>
</section>
{% endblock %}
```

Benzer şekilde, `author` view'i de aşağıdaki şekilde olmalıdır:

```
def author(request, id):
    author = Author.objects.get(idx=id)
    return render(request, 'author.html', context={"author": author})
```

`author.html` ise aşağıdaki şekilde olmalıdır:

```
{% extends "_base.html" %}

{% load static %}

{% block content %}
<section class="about_section layout_padding">
  <div class="container ">
    <div class="row">
      <div class="col-md-5">
      </div>
      <div class="col-md-5">
        <div class="detail-box">
          <div class="heading_container">
            <h2>
              {{ author.name }}
            </h2>
          </div>
          <p>
            {{ author.description }}
          </p>
        </div>
      </div>
    </div>
  </div>
</section>
</div>
{% endblock %}
```

### Kitap yorumlarının oluşturulması

`books/models.py` dosyasına aşağıdaki model eklenir:

```
class BookComment(models.Model):
    username = models.CharField(max_length=30)
    comment = models.CharField(max_length=1000)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
```

Model eklendikten sonra,

```
python manage.py makemigrations

python manage.py migrate
```

komutları ile veritabanına yazdırılır.

`book.html` dosyasına aşağıdaki yorumlar kısmı eklenir:

```
<div class="heading_container heading_center">
  <h3 class="mb-3">
    Comments
  </h3>
</div>
<div class="row d-flex justify-content-center">
  <div class="col-md-8 col-lg-6">
    <div class="card shadow-0 border" style="background-color: #f0f2f5;">
      <div class="card-body p-4">
        <div class="form-outline mb-4">
          <form class="" action="{% url 'sendComment' %}" method="POST">
            {% csrf_token %}
            {{ comment_form }}
            <input type="hidden" name="book_id" value="{{ book.idx }}">
            <button class="bg-info" type="submit">Send</button>
          </form>
        </div>

        <div class="card">
          <div class="card-body">
            <p>Comment example</p>

            <div class="d-flex justify-content-between">
              <div class="d-flex flex-row align-items-center">
                <p class="small mb-0 ms-2">Username</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

`books/forms.py` dosyası oluşturulur ve yorum formu eklenir:

```
from django import forms

class CommentForm(forms.Form):
    username = forms.CharField(label='Your name', max_length=30)
    comment = forms.CharField(label='Comment', max_length=500)
```

`books/views.py` dosyasında book viewi aşağıdaki şekilde değiştirilir:

```
from .forms import CommentForm

def book(request, id):
    book = Book.objects.get(idx=id)
    comment_form = CommentForm()
    return render(request, 'book.html', context={"book": book, "comment_form": comment_form})

```

Yorum POST request ile gönderildiğinde bu isteği alacak view de aynı dosyada yazılır:

```
from .models import BookComment
from django.shortcuts import redirect

def sendComment(request):
    if request.method == "POST":
        username = request.POST.get("username")
        comment = request.POST.get("comment")
        book_id = int(request.POST.get("book_id"))
        book = Book.objects.get(idx=book_id)
        book_comment = BookComment(username=username, comment=comment, book=book)
        book_comment.save()
        return redirect("book", book_id)
```

`books/urls.py` dosyasında oluşturulan view için path eklenir:

`path("sendComment", views.sendComment, name="sendComment")`

Yorum gönderme kısmı tamamlandı, şimdi varolan yorumların listelenmesi için book viewine aşağıdaki gibi bir değişiklik yapılır:

```
def book(request, id):
    book = Book.objects.get(idx=id)
    comment_form = CommentForm()
    comments = BookComment.objects.filter(book=book)
    return render(request, 'book.html', context={"book": book, "comment_form": comment_form, "comments": comments})
```

`book.html` dosyasında aşağıdaki değişiklik ile yorumlar listelenir:

```
        {% for comment in comments %}
        <div class="card">
          <div class="card-body">
            <p>{{ comment.comment }}</p>

            <div class="d-flex justify-content-between">
              <div class="d-flex flex-row align-items-center">
                <p class="small mb-0 ms-2">{{ comment.username }}</p>
              </div>
            </div>
          </div>
        </div>
        {% endfor %}
```
