from django.shortcuts import render

from goods.models import *

def get_path(categoryId):
    path=[categoryId,]
    while path[-1]!='':
        for c in Category.objects.filter(categoryId=path[-1]):
            path.append(c.parentId)
    return path

def get_category_list(categoryId):
    path=get_path(categoryId)
    category_list = []
    for pId in path:
        for element in Category.objects.filter(parentId=pId):
            if element.offer_count>0:
                category_list.append(element)
    return category_list

def get_path_list(categoryId):
    path=get_path(categoryId)
    path.reverse()
    path_list = []
    for pId in path:
        if pId!='':
            categorylist=Category.objects.filter(categoryId=pId)
            if len(categorylist)>0:
                path_list.append(categorylist[0])
    return path_list

def get_offer_list(categoryId):
    path=get_path(categoryId)
    path.reverse()
    offer_list = []
    if categoryId!='':
        for c in Category.objects.filter(categoryId=path[-1]):
            for o in Offer.objects.filter(categoryId=c):
                offer_list.append({'offer':o,'category':categoryId,'picture':get_picture(o.id)})
    return offer_list

def get_offer(offerId):
    offerlist=Offer.objects.filter(id=offerId)
    if len(offerlist)>0:
        return offerlist[0]
    else:
        return []

def get_picture(offerId):
    piclist=Picture.objects.filter(offer=get_offer(offerId))
    if len(piclist)>0:
        return piclist[0]
    else:
        return []                    

def index(request):
    context = {
        'category_list':get_category_list(''),
        'path_list':get_path_list(''),
        'offer_list':get_offer_list('')}
    return render(request, 'goods/index.html', context)

def category(request, categoryId):
    context = {
        'category_list':get_category_list(categoryId),
        'path_list':get_path_list(categoryId),
        'offer_list':get_offer_list(categoryId)[:5]}
    return render(request, 'goods/index.html', context)

def offer(request, categoryId, offerId):
    context = {
        'category_list':get_category_list(categoryId),
        'path_list':get_path_list(categoryId),
        'offer':get_offer(offerId),
        'picture':get_picture(offerId)}
    return render(request, 'goods/index.html', context)
