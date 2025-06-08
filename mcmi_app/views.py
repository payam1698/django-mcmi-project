from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Item
from .forms import ItemForm # We'll create this form in a later step

# Item CRUD views
@login_required
def item_list(request):
    items = Item.objects.all()
    return render(request, 'mcmi_app/item_list.html', {'items': items})

@login_required
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'mcmi_app/item_detail.html', {'item': item})

@login_required
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'mcmi_app/item_form.html', {'form': form})

@login_required
def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm(instance=item)
    return render(request, 'mcmi_app/item_form.html', {'form': form})

@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'mcmi_app/item_confirm_delete.html', {'item': item})

# Authentication views
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('item_list')
    else:
        form = UserCreationForm()
    return render(request, 'mcmi_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('item_list')
    else:
        form = AuthenticationForm()
    return render(request, 'mcmi_app/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login') # Redirect to login page after logout
    # For GET request, you might want to show a confirmation page or simply redirect
    # For simplicity, redirecting to login if accessed via GET,
    # but a POST request is more standard for logout.
    return redirect('login')
