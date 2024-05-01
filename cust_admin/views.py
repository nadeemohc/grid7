from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from accounts.models import User
from cust_auth_admin.views import admin_required
from store.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
from django.db.models import Case, CharField, Value, When


@admin_required
def dashboard(request):
    product_count = Product.objects.count()
    cat_count = Category.objects.count()
    context = {
        'title': 'Admin Dashboard',
        'product_count': product_count,
        'cat_count': cat_count,
    }
    return render(request, 'cust_admin/index.html', context)

#=========================================== admin list, view, delete user =========================================================================================================

@admin_required
def user_list(request):
    users = User.objects.all().order_by('id')
    context={
        'title':'User List',
         'users': users,
         }
    return render(request, 'cust_admin/user/user_list.html', context)


@admin_required
def user_view(request, username):
    user = get_object_or_404(User, username=username)
    context = {
        'title': 'View User',
        'user': user
        }
    return render(request, 'cust_admin/user/user_view.html', context)

User = get_user_model()


@admin_required
def user_block_unblock(request, username):
    user = get_object_or_404(User, username = username)
    user.is_active = not user.is_active
    user.save()
    action = 'blocked' if not user.is_active else 'unblocked'
    messages.success(request, f"The user {user.username} has been {action} successfully.")
    return redirect('cust_admin:user_list')

#=========================================== admin add, list, edit, delete category=========================================================================================================

@admin_required
def category_list(request):
    categories = Category.objects.all().order_by('c_id')
    context = {
        'title':'Category List',
        'categories':categories,
        }
    return render(request, 'cust_admin/category/category_list.html', context)


@admin_required
def add_category(request):
    context = {
        'title': 'Add Category'
    }

    if request.method == 'POST':
        c_name = request.POST.get('cname')
        c_image = request.FILES.get('image')

        # Check if a category with the same name already exists
        existing_category = Category.objects.filter(c_name=c_name).exists()
        if existing_category:
            messages.error(request, f"Category {c_name} with this name already exists.")
        else:
            # Create and save the new category
            c_data = Category(c_name=c_name, c_image=c_image)
            c_data.save()
            messages.success(request, "Category added successfully.")
            return redirect('cust_admin:category_list')

    return render(request, 'cust_admin/category/add_category.html', context)



@admin_required
def category_list_unlist(request, c_id):
    category = get_object_or_404(Category, c_id = c_id)
    category.is_blocked = not category.is_blocked    
    category.save()
    action = 'unblocked' if not category.is_blocked else 'blocked'
    messages.success(request, f"The category with ID {category.c_id} has been {action} successfully.")
    return redirect('cust_admin:category_list')


@admin_required
def edit_category(request, c_id):
    category = get_object_or_404(Category, c_id=c_id)
    if request.method == 'POST':
        category.c_name = request.POST.get('cname')
        category.c_image = request.FILES.get('image')
        # is_blocked = request.POST.get('blocked')

        
        category.save()
        context = {
            'title':'Add Category'
            }
        return redirect('cust_admin:category_list')
          
    return render(request, 'cust_admin/category/category_edit.html', context)

#=========================================== admin add, list subcategory =========================================================================================================

@admin_required
def subcategory_list(request):
    sub_cat = Subcategory.objects.all()
    context = {
        'title':'Sub Category',
        'sub_cat':sub_cat,
               }
    return render(request,'cust_admin/sub_category/sub_cat_list.html', context)


@admin_required
def add_subcat(request):
    if request.method == 'POST':
        sub_name = request.POST.get('sub_name')
        # c_id = request.POST.get('category')
        # category = Category.objects.get(c_id = c_id)
        Subcategory.objects.create(sub_name = sub_name)
        return redirect('cust_admin:subcategory_list')
    # categories = Category.objects.all()
    return render(request, 'cust_admin/sub_category/add_sub_cat.html', {'title':'Add Sub Category'})

#=========================================== admin add, list, edit, delete product =========================================================================================================

@admin_required
def add_product(request):
    if request.method == 'POST':
        # Extract data from the form
        title = request.POST.get('title')
        image = request.FILES.getlist('image')
        description = request.POST.get('description')
        price = request.POST.get('price')
        old_price = request.POST.get('old_price')
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')
        stock = request.POST.get('stock')
        shipping = request.POST.get('ship')
        specifications = request.POST.get('add_det')

        # Checkboxes
        popular = request.POST.get('popular') == 'on'
        featured = request.POST.get('featured') == 'on'
        latest = request.POST.get('latest') == 'on'
        in_stock = request.POST.get('in_stock') == 'on'
        status = request.POST.get('status') == 'on'

        # Get the category and subcategory objects
        category = get_object_or_404(Category, c_id=category_id)
        subcategory = get_object_or_404(Subcategory, sid=subcategory_id)

        # Get the selected sizes from the form
        selected_sizes_ids = request.POST.getlist('sizes')
        selected_sizes = Size.objects.filter(id__in=selected_sizes_ids)

        # Create the product
        product = Product.objects.create(
            title=title,
            image=image[0],
            description=description,
            price=price,
            old_price=old_price,
            category=category,
            sub_category=subcategory,
            stock=stock,
            shipping=shipping,
            specifications=specifications,
            popular=popular,
            featured=featured,
            latest=latest,
            in_stock=in_stock,
            status=status,
        )

        # Add selected sizes to the product
        product.size.set(selected_sizes)

        # Save additional images
        for i in image[1:]:
            try:
                ProductImages.objects.create(product=product, images=i)
            except Exception as e:
                print(e)

        messages.success(request, 'Product added successfully!')
        return redirect('cust_admin:prod_list')

    # Fetch categories, subcategories, and sizes for dropdowns and selects
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    sizes = Size.objects.all()

    context = {
        'categories': categories,
        'subcategories': subcategories,
        'sizes': sizes,
    }

    return render(request, 'cust_admin/product/product_add.html', context)


@admin_required
def prod_edit(request, p_id):
    product = get_object_or_404(Product, p_id=p_id)
    product_images = ProductImages.objects.filter(product=product)

    if request.method == 'POST':
        # Update product details
        product.title = request.POST.get('title', product.title)
        product.description = request.POST.get('description', product.description)
        product.old_price = request.POST.get('old_price', product.old_price)
        product.price = request.POST.get('price', product.price)
        product.category_id = request.POST.get('category', product.category)
        # product.subcategory_id = request.POST.get('subcategory_id', product.subcategory)  
        product.stock = request.POST.get('stock', product.stock)
        product.shipping = request.POST.get('shipping', product.shipping)
        product.specifications = request.POST.get('specifications', product.specifications)
        product.featured = request.POST.get('featured') == 'on'
        product.popular = request.POST.get('popular') == 'on'
        product.latest = request.POST.get('latest') == 'on'
        product.in_stock = request.POST.get('in_stock') == 'on'
        product.status = request.POST.get('status') == 'on'
        # Handle image update
        new_image = request.FILES.get('image')
        print(new_image)
        if new_image:
            product.image = new_image
        product.save()


        return redirect('cust_admin:prod_list')
        

    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    context = {'title':'Edit Product',
                    'product':product,
                    'categories':categories,
                    'subcategories':subcategories,
                    'product_images':product_images}
    return render (request, 'cust_admin/product/product_edit.html',context)


@admin_required
def product_list_unlist(request, p_id):
    product = get_object_or_404(Product, pk = p_id)
    product.is_blocked = not product.is_blocked
    product.save()
    action = 'unblocked' if not product.is_blocked else 'blocked'
    messages.success(request, f"The category with ID {product.p_id} has been {action} successfully.")
    return redirect('cust_admin:prod_list')


@admin_required
def prod_list(request):
    products = Product.objects.all().order_by('p_id')
    
    context = {
        'products': products,
        'title': 'Product List'
    }
    return render(request, 'cust_admin/product/product_list.html', context)

#=========================================== admin add, list, edit, delete product =========================================================================================================

def list_variant(request):
    # Define the custom ordering based on the size values
    custom_ordering = Case(
        When(size='S', then=Value(0)),
        When(size='M', then=Value(1)),
        When(size='L', then=Value(2)),
        When(size='XL', then=Value(3)),
        When(size='XXL', then=Value(4)),
        default=Value(5),
        output_field=CharField(),
    )

    # Fetch the Size objects ordered according to the custom ordering
    data = Size.objects.all().order_by(custom_ordering)

    context = {
        'data': data,
        'title': 'Variant List',
    }
    return render(request, 'cust_admin/variant/variant_list.html', context)

def add_variant(request):
    if request.method == 'POST':
        size = request.POST.get('size')
        price_increment = request.POST.get('price_inc')

        try:
            existing_size = Size.objects.filter(size__iexact=size)
            if existing_size:
                messages.error(request, "The size already exists")
            else:
                new_size = Size(size = size, price_increment = price_increment)
                new_size.save()
                messages.success(request, f'The size {size} added Succesfully')
        except IntegrityError:
            messages.error(request, 'An error occured while adding the size')
        
        return redirect('cust_admin:list_variant')
    context = {
            'title': 'Variant Add',
        }
    return render(request, 'cust_admin/variant/variant_add.html', context)


def edit_variant(request, id):
    if request.method == 'POST':
        size = request.POST.get('size')
        price_increment = request.POST.get('price_inc')
        edit=Size.objects.get(id=id)
        edit.size = size
        edit.price_increment = price_increment
        edit.save()
        return redirect('cust_admin:list_variant')
    obj = Size.objects.get(id=id)
    context = {
        "obj":obj,
        'title': 'Variant Edit',
    }
    
    return render(request, 'cust_admin/variant/variant_edit.html', context)