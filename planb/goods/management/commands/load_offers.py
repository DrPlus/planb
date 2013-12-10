from django.core.management.base import BaseCommand, CommandError
import xml.dom.minidom
import PIL
import urllib.request
from datetime import datetime
import time
from django.utils.timezone import utc
from goods.models import *
from planb import settings

class Command(BaseCommand):
    help = 'Loads data'

    def handle(self, *args, **options):
        dom = xml.dom.minidom.parse('c:/www/planb/static/div_kid.xml')

        yml_catalog = dom.getElementsByTagName('yml_catalog')[0]
        x_shop = yml_catalog.getElementsByTagName('shop')[0]
        dt = datetime.strptime(yml_catalog.getAttribute('date'),'%Y-%m-%d %H:%M').replace(tzinfo=utc)
        load_shop(x_shop, dt)

def clear_shop(t_shop):
    for o in Offer.objects.filter(
        shop__name=t_shop['name'],
        shop__company=t_shop['company'],
        shop__url=t_shop['url']
        ):
        o.delete()
    for c in Category.objects.filter(
        shop__name=t_shop['name'],
        shop__company=t_shop['company'],
        shop__url=t_shop['url']
        ):
        c.delete()
    for s in Shop.objects.filter(
        name=t_shop['name'],
        company=t_shop['company'],
        url=t_shop['url']
        ):
        s.delete()

def load_shop(x_shop, dt):
    t_shop = {'name':'', 'company':'', 'url':'','date':datetime(1900,1,1,0,0)}
    t_shop['name'] = x_shop.getElementsByTagName('name')[0].childNodes[0].data
    t_shop['company'] = x_shop.getElementsByTagName('company')[0].childNodes[0].data
    t_shop['url'] = x_shop.getElementsByTagName('url')[0].childNodes[0].data
    t_shop['date'] = dt

    start = time.clock()
    print('Clearing...')
    clear_shop(t_shop)
    print(str(time.clock() - start))
    shop = Shop(
        name=t_shop['name'],
        company=t_shop['company'],
        url=t_shop['url'],
        date=t_shop['date']
        )
    shop.save()    
    load_currencies(x_shop, shop)
    load_categories(x_shop, shop)
    start = time.clock()
    print('Loading offers...')
    load_offers(x_shop, shop)
    print(str(time.clock() - start))
    start = time.clock()
    print('Calculating offers...')
    count_offers()
    print(str(time.clock() - start))

def count_offers():
    def get_offer_count(category):
        if category.offer_count > 0:
            return category.offer_count
        else:
            cnt = Offer.objects.filter(categoryId=category).count()
            for c in Category.objects.filter(parentId=category.categoryId):
                cnt = cnt + get_offer_count(c)
            return cnt
    
    for c in Category.objects.all():
        c.offer_count = get_offer_count(c)
        c.save()

def load_currencies(x_shop, shop):
    for element in x_shop.getElementsByTagName('currencies')[0].getElementsByTagName('currency'):
        t_currency = {'cur_id':'', 'rate':0, 'plus':0}
        t_currency['cur_id'] = element.getAttribute('id')
        try:
            t_currency['rate'] = float(element.getAttribute('rate'))
        except ValueError:
            t_currency['rate'] = 1
        try:
            t_currency['plus'] = float(element.getAttribute('plus'))
        except ValueError:
            t_currency['plus'] = 0
        currency= Currency(
            shop = shop,
            cur_id = t_currency['cur_id'],
            rate = t_currency['rate'],
            plus = t_currency['plus']
            )
        currency.save()
    
def load_categories(x_shop, shop):
    for element in x_shop.getElementsByTagName('categories')[0].getElementsByTagName('category'):
        t_category = {'categoryId':'', 'parentId':'', 'category':''}
        t_category['categoryId'] = element.getAttribute('id')
        t_category['parentId'] = element.getAttribute('parentId')
        t_category['category'] = element.childNodes[0].data
        category = Category(
            shop=shop,
            categoryId = t_category['categoryId'],
            parentId = t_category['parentId'],
            category = t_category['category'],
            offer_count = 0)
        category.save()
        
def load_offers(x_shop, shop):
    for element in x_shop.getElementsByTagName('offers')[0].getElementsByTagName('offer'):
        t_offer = {
            'offer_id':'',
            'type':'',
            'url':'',
            'price':0,
            'currencyId':'',
            'categoryId':[],
            'name':'',
            'vendor':'',
            'vendorCode':'',
            'description':''}

        t_offer['offer_id'] = element.getAttribute('id')
        if element.getElementsByTagName('type')==[]:
            t_offer['type']='none'
        else:
            t_offer['type']=element.getElementsByTagName('type')[0].childNodes[0].data
        t_offer['url']=getCharData(element,'url')
        t_offer['price'] = float(element.getElementsByTagName('price')[0].childNodes[0].data)
        t_offer['currencyId'] = element.getElementsByTagName('currencyId')[0].childNodes[0].data
        for cnode in element.getElementsByTagName('categoryId'):
            t_offer['categoryId'].append(cnode.childNodes[0].data)

        t_offer['name']=getCharData(element,'name')
        t_offer['vendor']=getCharData(element,'vendor')
        t_offer['vendorCode']=getCharData(element,'vendorCode')
        t_offer['description']=getCharData(element,'description')

        if len(t_offer['description'])>1000:
            t_offer['description']=t_offer['description'][:1000]

        offer = Offer(
            shop = shop,
            offer_id = t_offer['offer_id'],
            type = t_offer['type'],
            url = t_offer['url'],
            price = t_offer['price'],
            currencyId = t_offer['currencyId'],
            name = t_offer['name'],
            vendor = t_offer['vendor'],
            vendorCode = t_offer['vendorCode'],
            description = t_offer['description']
            )
        offer.save()

        for categoryId in t_offer['categoryId']:
            categories = Category.objects.filter(categoryId=categoryId)
            if categories != []:
                offer.categoryId.add(categories[0])

        if t_offer['type'] in ['book','audiobook']:
            load_book_offer(element, offer)
        if t_offer['type'] in ['artist.title']:
            load_artist_offer(element, offer)
        load_picture(element, offer)

def load_book_offer(element, offer):
    t_book_offer = {
        'author':'',
        'publisher':'',
        'series':'',
        'year':'',
        'ISBN':'',
        'volume':'',
        'part':'',
        'language':'',
        'performed_by':'',
        'performance_type':'',
        'storage':''}
    
    for name in t_book_offer.keys():
        t_book_offer[name]=getCharData(element, name)
    book_offer = BookOffer(
        offer = offer,
        author = t_book_offer['author'],
        publisher = t_book_offer['publisher'],
        series = t_book_offer['series'],
        year = t_book_offer['year'],
        ISBN = t_book_offer['ISBN'],
        volume = t_book_offer['volume'],
        part = t_book_offer['part'],
        language = t_book_offer['language'],
        performed_by = t_book_offer['performed_by'],
        performance_type = t_book_offer['performance_type'],
        storage = t_book_offer['storage']
    )
    book_offer.save()

def load_artist_offer(element, offer):
    t_artist_offer = {
        'title':'',
        'year':'',
        'media':'',
        'artist':'',
        'starring':'',
        'director':'',
        'originalName':'',
        'country':''}
    
    for name in t_artist_offer.keys():
        t_artist_offer[name]=getCharData(element, name)
    artist_offer = ArtistOffer(
        offer = offer,
        title = t_artist_offer['title'],
        year = t_artist_offer['year'],
        media = t_artist_offer['media'],
        artist = t_artist_offer['artist'],
        starring = t_artist_offer['starring'],
        director = t_artist_offer['director'],
        originalName = t_artist_offer['originalName'],
        country = t_artist_offer['country']
    )
    artist_offer.save()    

def load_picture(element, offer):
    for pic in element.getElementsByTagName('picture'):
        picture = Picture(
            offer = offer,
            picture_url = pic.childNodes[0].data
            )
        picture.save()

def getCharData(element, name):
    if element.getElementsByTagName(name)==[]:
        return ''
    else:
        return element.getElementsByTagName(name)[0].childNodes[0].data
