from django.shortcuts import render, redirect
from store.models import Category, Product, ProductImages
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache

# Create your views here.

@never_cache
def home(request):
    categories = Category.objects.all()
    Products = Product.objects.all()
    # featured_products = Product.objects.filter(featured=True)
    # popular_products = Product.objects.filter(popular=True)
    # new_added_products = Product.objects.filter(latest=True)
    return render(request, 'dashboard/home.html', 
                  {'title':'Home',
                   'categories':categories,
                   'products':Products})


def handler404(request, exception):
    return render(request, '404.html', status=404)

@never_cache
def product_detail(request,product_pid):    
    product = get_object_or_404(Product, p_id=product_pid)
    product_images = ProductImages.objects.filter(product=product)
    print(product_images)

    context = {
        'product': product,
        'product_images': product_images,
   
    }

    return render(request, 'core/product_detail.html',context)

# def product_detailed_view(request, product_id):
#     product = Product.objects.get(p_id=product_id)
    
#     # Pass the product object to the template context
#     context = {
#         'product': product
#     }
#     return render(request, 'dashboard/product_detailed_view.html', context)


def product_detailed_view(request,product_pid):
    product = get_object_or_404(Product, p_id=product_pid)
    product_images = ProductImages.objects.filter(product=product)
    print(product_images)

    context = {
        'product': product,
        'product_images': product_images,
        'breadcrumb': product.title,
   
    }

    return render(request, 'dashboard/product_detailed_view.html',context)

def prod_det_view(request, product_id):
    # Assuming you have a Product model with an id field
    product = Product.objects.get(id=product_id)
    
    # Fetch all the images associated with the product
    product_images = ProductImages.objects.filter(product_id=product_id)
    print(product_images)
    
    return render(request, 'product_detail.html', {'product': product, 'product_images': product_images})