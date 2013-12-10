from django.db import models
from django.core.files import File
from PIL import Image
from planb import settings
import os

def image_file_name(instance, filename): 
    fname= '/'.join(['images', instance.offer.shop.name, filename])
    afolder = os.path.join(settings.MEDIA_ROOT, 'images/%s'%instance.offer.shop.name)
    if not os.path.exists(afolder):
        os.makedirs(afolder)
    return fname

class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name = "Название")
    company = models.CharField(max_length=200, verbose_name = "Компания")
    url = models.URLField(max_length=200, verbose_name = "URL главной страницы")
    date = models.DateTimeField(verbose_name = "Дата и время генерации каталога")

    def __str__(self):
        return self.name

class Currency(models.Model):
    CURRENCY_CHOICES = (('RUR','Рубль'),('RUB','Рубль'),('USD','Доллар США'),('BYR','Белорусский рубль'),('KZT','Тенге'),('EUR','Евро'),('UAH','Гривна'))
    shop = models.ForeignKey(Shop)
    cur_id = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='RUR', verbose_name = "Код валюты")
    rate = models.FloatField(verbose_name = "Курс")
    plus = models.FloatField(verbose_name = "Надбавка к курсу, в %", default=0)

    def __str__(self):
        return self.cur_id

class Category(models.Model):
    shop = models.ForeignKey(Shop)
    categoryId = models.CharField(max_length=20, verbose_name = "Идентификатор")
    parentId = models.CharField(max_length=20, verbose_name = "Идентификатор родительской категории", blank=True)
    category = models.CharField(max_length=100, verbose_name = "Категория")
    offer_count = models.IntegerField(verbose_name = "Количество товаров в категории")
        
    def __str__(self):
        return self.category+' '+str(self.offer_count)
    
class Offer(models.Model):
    TYPE_CHOICES = (('none','Упрощенное описание'), ('vendor.model','Произвольный товар (vendor.model)'), ('book','Книги'), ('audiobook','Аудиокниги'), ('artist.title','Музыкальная и видео продукция'), ('tour','Туры'), ('ticket','Билеты'), ('event-ticket','Билеты на мероприятие'))
    CURRENCY_CHOICES = (('RUR','Рубль'),('RUB','Рубль'),('USD','Доллар США'),('BYR','Белорусский рубль'),('KZT','Тенге'),('EUR','Евро'),('UAH','Гривна'))
    shop = models.ForeignKey(Shop)
    offer_id = models.CharField(max_length=20, verbose_name = "Идентификатор", blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name = "Тип товара")
    url = models.URLField(max_length=200, verbose_name = "URL товара")
    price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name = "Цена")
    currencyId = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='RUR', verbose_name = "Код валюты")
    categoryId = models.ManyToManyField(Category)
    name = models.CharField(max_length=200, verbose_name = "Название товарного предложения", blank=True)
    vendor = models.CharField(max_length=200, verbose_name = "Производитель", blank=True)
    vendorCode = models.CharField(max_length=200, verbose_name = "Код товара", blank=True)
    description = models.CharField(max_length=1000, verbose_name = "Описание", blank=True)

    def __str__(self):
        if self.name=='':
            if self.vendorCode=='':
                return self.description
            else:
                return self.vendorCode
        else:
            return self.name

class BookOffer(models.Model):
    offer = models.ForeignKey(Offer)
    author = models.CharField(max_length=100, verbose_name = "Автор", blank=True)
    publisher = models.CharField(max_length=100, verbose_name = "Издательство", blank=True)
    series = models.CharField(max_length=100, verbose_name = "Серия", blank=True)
    year = models.CharField(max_length=10, verbose_name = "Год издания", blank=True)
    ISBN = models.CharField(max_length=100, verbose_name = "Код", blank=True)
    volume = models.CharField(max_length=100, verbose_name = "Количество томов", blank=True)
    part = models.CharField(max_length=100, verbose_name = "Номер тома", blank=True)
    language = models.CharField(max_length=100, verbose_name = "Язык произведения", blank=True)
    performed_by = models.CharField(max_length=100, verbose_name = "Исполнитель аудиокниги", blank=True)
    performance_type = models.CharField(max_length=100, verbose_name = "Тип аудиокниги", blank=True)
    storage = models.CharField(max_length=100, verbose_name = "Носитель аудиокниги", blank=True)    

    def __str__(self):
        return self.author
    
class ArtistOffer(models.Model):
    offer = models.ForeignKey(Offer)
    title = models.CharField(max_length=100, verbose_name = "Название", blank=True)
    year = models.CharField(max_length=10, verbose_name = "Год издания", blank=True)
    media = models.CharField(max_length=100, verbose_name = "Носитель", blank=True)
    artist = models.CharField(max_length=100, verbose_name = "Исполнитель (для музыки/видео)", blank=True)
    starring = models.CharField(max_length=100, verbose_name = "Актеры (для фильма)", blank=True)
    director = models.CharField(max_length=100, verbose_name = "Режиссер (для фильма)", blank=True)
    originalName = models.CharField(max_length=100, verbose_name = "Оригинальное название (для фильма)", blank=True)
    country = models.CharField(max_length=100, verbose_name = "Страна (для фильма)", blank=True)

    def __str__(self):
        return self.title
    
class Picture(models.Model):
    offer = models.ForeignKey(Offer)
    picture_url = models.URLField(max_length=200, verbose_name = "URL картинки")
    picture_local = models.ImageField(upload_to=image_file_name, verbose_name = "Локальная копия", blank=True)

    def __str__(self):
        if self.offer.name=='':
            if self.offer.vendorCode=='':
                return self.offer.description
            else:
                return self.offer.vendorCode
        else:
            return self.offer.name
