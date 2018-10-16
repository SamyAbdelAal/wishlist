from django.shortcuts import render, redirect
from items.models import Item, FavoriteItem
from django.db.models import Q
from .forms import UserRegisterForm, UserLoginForm
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse 

# Create your views here.
def item_list(request):
    if not request.user.is_authenticated:
        return redirect('user-login')
    items = Item.objects.all()
    query = request.GET.get('q')
    if query:
        items = items.filter(
        Q(name__icontains=query)|
        Q(description__icontains=query)
        ).distinct()

    my_fav = []
    for favorite in FavoriteItem.objects.filter(user = request.user):
        my_fav.append(favorite.item.id)   
    context = {
        "items": items,
        "my_favs": my_fav,
    }
    return render(request, 'item_list.html', context)

def item_detail(request, item_id):
    context = {
        "item": Item.objects.get(id=item_id)
    }
    return render(request, 'item_detail.html', context)

def user_register(request):
    register_form = UserRegisterForm()
    if request.method == "POST":
        register_form = UserRegisterForm(request.POST)
        if register_form.is_valid():
            user = register_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            login(request, user)
            return redirect('item-list')
    context = {
        "register_form": register_form
    }
    return render(request, 'user_register.html', context)

def user_login(request):
    login_form = UserLoginForm()
    if request.method == "POST":
        login_form = UserLoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            authenticated_user = authenticate(username=username, password=password)
            if authenticated_user:
                login(request, authenticated_user)
                return redirect('item-list')
    context = {
        "login_form": login_form
    }
    return render(request, 'user_login.html', context)

def user_logout(request):
    logout(request)

    return redirect('item-list')

def item_favorite(request, item_id):
    item = Item.objects.get(id=item_id)
    favorite , created = FavoriteItem.objects.get_or_create(item= item, user=request.user)
    if created:
        action= "like"
    else:
        action="unlike"
        favorite.delete()
    data = {
    "action": action
    }
    return JsonResponse(data)


def favorite_items(request):
    if not request.user.is_authenticated:
        return redirect('user-login')
    items = FavoriteItem.objects.filter(user=request.user)
    query = request.GET.get('q1')
    if query:
        items = items.filter(
        Q(item__name__icontains=query)|
        Q(item__description__icontains=query)
        ).distinct()
    # my_fav = []
    # for favorite in FavoriteItem.objects.filter(user = request.user):
    #     my_fav.append(favorite.item)   
    context = {
        # "my_fav": my_fav,
        "items": items,
    }
    return render(request, 'fav_list.html', context)