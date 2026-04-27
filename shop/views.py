from django.shortcuts import render, redirect
from .models import Product, Category
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Order, OrderItem

def catalog(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query)

    sort_by = request.GET.get('sort', '')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')

    category_slug = request.GET.get('category', '')
    if category_slug and category_slug != 'all':
        products = products.filter(category__slug=category_slug)
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'sort_by': sort_by,
        'selected_category': category_slug,
    }
    return render(request, 'shop/catalog.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'shop/login.html'
    redirect_authenticated_user = True

def get_cart(request):
    """Получить или создать корзину"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_cart(request)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('/cart/')

def cart_view(request):
    cart = get_cart(request)
    cart_items = cart.items.all()
    total = sum(item.total_price() for item in cart_items)
    
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total,
    })

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('/cart/')

def checkout(request):
    cart = get_cart(request)
    cart_items = cart.items.all()
    
    if not cart_items:
        return redirect('/cart/')
    
    if request.method == 'POST':
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        total = sum(item.total_price() for item in cart_items)
        
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            phone=phone,
            address=address,
            total_price=total,
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        
        cart_items.delete()
        return redirect('/')
    
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total': total,
    })

def profile(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/profile.html', {'orders': orders})