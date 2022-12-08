# Projenin Canlıya Alınması (Deployment)
Projeyi canlıya almak için bir Linux sunucusuna ihtiyacımız var. Amazon Web Services (AWS), kayıt olduktan sonra 12 ay boyunca ücretsiz sunucu kullanılması imkanını sağlıyor (EC2 instance-free tier). Aşağıdaki adımları oradan bir instance oluşturup uygulayabilirsiniz.

https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html

## settings.py Değişiklikleri
Ana app'imizde (book_platform klasörü) bulunan settings.py dosyasında birkaç değişiklik yapmalıyız.

### DEBUG
`DEBUG` değişkeni yalnızca projeyi geliştirirken `True` olmalıdır. Bu nedenle `DEBUG = False` olmalıdır.

### ALLOWED_HOSTS
Projemizi çıkaracağımız domain adını veya domainimiz yoksa IP'sini `ALLOWED_HOSTS` listesine eklemeliyiz. Örneğin:

`ALLOWED_HOSTS = ['bookplatform.com', '45.120.90.3']`

### Static Dosyaların Toplanması
Static dosyaların servis edilmesi için tek bir klasörde toplanması gerekmektedir. Hangi klasörde toplanacağını belirtmemiz gerekmektedir. Bunun için aşağıdaki satır `settings.py`'a eklenmelidir:

```
STATIC_ROOT = BASE_DIR / "statics"
```

Daha sonra static dosyaları toplamak için `python manage.py collectstatic` komutunu kullanabiliriz.

## WSGI
Django, production'da (canlıda) kullanılmaya uygun bir webserver içermediğinden dolayı, kendi webserverimizi (Apache veya Nginx) kurup projemizi bu webserver'a bağlamalıyız. Fakat bir webserver kursak bile bu webserver Python kodunu okuyamaz. Bunun üstesinden gelmek için WSGI (Webserver Gateway Interface) denilen arayüzleri kullanabiliriz. `Gunicorn` bu arayüzlerden birisidir. Ayrıca Gunicorn, webserver yazılımlarının (Apache ve Nginx) özelliklerinden bazılarına sahip olduğu için, webserver kullanmadan direkt Gunicorn kullanmak da küçük projeler için yeterlidir, fakat biz webserver da kuracağız. Aşağıdaki şema özetlemektedir:

<p align="center">
    <img src="https://github.com/ituacm/ITU-ACM-22-23-Django-Workshop/blob/main/doc/deployment_diagram.png?raw=true" alt="drawing" width="800"/>
</p>
    
## Gunicorn'un Yüklenmesi
Aşağıdaki komut ile pip'ten yüklenir.

```
pip install gunicorn
```

## Nginx'in Kurulması
Nginx, en çok kullanılan 2 web sunucusundan birisidir (diğeri Apache'dir). Aşağıdaki komut ile yüklenir:

`sudo apt install nginx`

İndirdikten sonra güvenlik duvarından (firewall) Nginx'e izin vermeliyiz. Nginx, `ufw` adındaki firewall sistemi ile birlikte çalışmaktadır. Aşağıdaki komut ile kullanılabilecek güvenlik profilleri listelenebilir:

```
sudo ufw app list
```

Çıktı:

```
Available applications:
  Nginx Full
  Nginx HTTP
  Nginx HTTPS
  OpenSSH
```

Aşağıdaki komut ile izin verilir:

`sudo ufw allow 'Nginx Full'`

Şimdi sunucumuza tarayıcıdan girdiğimizde aşağıdaki gibi bir ekranla karşılaşmalıyız:

<p align="center">
    <img src="https://github.com/ituacm/ITU-ACM-22-23-Django-Workshop/blob/main/doc/nginx_welcome.png?raw=true" alt="drawing" width="500"/>
</p>
    
### Nginx'te Static Dosyaların Servis Edilmesi
Django çalışırken static dosyalarımızı `http://<domainimiz>/static` adresinde arayacaktır. Bu nedenle Nginx'te `/static` dizinini az önce Django'da topladığımız static dosyaların bulunduğu path'e yönlendirmeliyiz. Bunun için 
`/etc/nginx/sites-enabled/default` dosyasını admin izinleriyle açıp `server` altına aşağıdaki ayarı kopyalayıp dizini değiştirmeliyiz:

```
location /static/ {
	alias <static dosyaların toplandığı dizin>;
}
```

### Gunicorn'un Çalıştırılması
Django projemiz ve web sunucumuz hazır olduğuna göre sıra bu ikisini bağlamaya geldi.

Django proje klasörüne girdikten sonra (manage.py dosyasının olduğu klasör) `gunicorn book_platform.wsgi` komutu girilir.

### Nginx ile Gunicorn'un Bağlanması
Şimdi ise Nginx ile Gunicorn'u bağlamalıyız. Bunun için sitemizin `/` dizinini Gunicorn'un çalıştığı adrese yönlendireceğiz. Yine `/etc/nginx/sites-enabled/default` dosyasında `server` altına aşağıdaki ayarı da kopyalıyoruz:

```
location / {
	proxy_pass http://127.0.0.1:8000;
      proxy_set_header X-Forwarded-Host $server_name;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_redirect off;
      add_header P3P 'CP="ALL DSP COR PSAa OUR NOR ONL UNI COM NAV"';
      add_header Access-Control-Allow-Origin *;
}
```

Bu dosyanın son hali aşağıdakine benzer olacaktır:

```
# Default server configuration
#
server {
        listen 80 default_server;
        listen [::]:80 default_server;

        location /static/ {
            alias /home/user/django-project/book_platform_con/statics/;
        }

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header X-Forwarded-Host $server_name;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_redirect off;
            add_header P3P 'CP="ALL DSP COR PSAa OUR NOR ONL UNI COM NAV"';
            add_header Access-Control-Allow-Origin *;
        }

        # SSL configuration
        #
        # listen 443 ssl default_server;
        # listen [::]:443 ssl default_server;
        #
        # Note: You should disable gzip for SSL traffic.
        # See: https://bugs.debian.org/773332
        #
        # Read up on ssl_ciphers to ensure a secure configuration.
        # See: https://bugs.debian.org/765782
        #
        # Self signed certs generated by the ssl-cert package
        # Don't use them in a production server!
        #
        # include snippets/snakeoil.conf;

        root /var/www/html;

        # Add index.php to the list if you are using PHP
        index index.html index.htm index.nginx-debian.html;

        server_name _;

        # pass PHP scripts to FastCGI server
        #
        #location ~ \.php$ {
        #       include snippets/fastcgi-php.conf;
        #
        #       # With php-fpm (or other unix sockets):
        #       fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
        #       # With php-cgi (or other tcp sockets):
        #       fastcgi_pass 127.0.0.1:9000;
        #}

        # deny access to .htaccess files, if Apache's document root
        # concurs with nginx's one
        #
        #location ~ /\.ht {
        #       deny all;
        #}
}


# Virtual Host configuration for example.com
#
# You can move that to a different file under sites-available/ and symlink that
# to sites-enabled/ to enable it.
#
#server {
#       listen 80;
#       listen [::]:80;
#
#       server_name example.com;
#
#       root /var/www/example.com;
#       index index.html;
#
#       location / {
#               try_files $uri $uri/ =404;
#       }
#}
```

Ayarları yaptıktan sonra Nginx'i yeniden başlatmamız gerekmektedir. Bunun için `sudo systemctl restart nginx` komutunu giriyoruz.

Ekstra bilgi olarak: Nginx ile sunacağımız sitemizin içeriği normalde `/var/www/html` klasöründe bulunur. Fakat biz Django kullandığımız için bu klasör ile bir işimiz yok.

## (Opsiyonel) Gunicorn'un Servis Olarak Eklenmesi
Şu anda Gunicorn çalıştıkça sitemiz de çalışıyor halde olacaktır. Fakat Gunicorn şu anda arka planda çalışması gerekirken normal şekilde çalışıyor. Arka planda çalışmasını sağlarsak sunucumuz her başladığında Gunicorn da başlar ve manuel olarak çalıştırmamıza gerek kalmaz. Linux'ta servis oluşturmak için aşağıdaki linki inceleyebilirsiniz:

https://linuxhandbook.com/create-systemd-services
