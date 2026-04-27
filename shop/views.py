from django.shortcuts import render
from .models import Product, Category

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