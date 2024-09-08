from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from accounts.models import User
from cust_auth_admin.views import admin_required
from store.models import *
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from cust_admin.forms import ProductVariantAssignForm, CouponForm, CategoryOfferForm, ProductOfferForm
from django.contrib import messages
from decimal import Decimal
import sweetify
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import IntegrityError
from PIL import Image
from django.db.models import Case, CharField, Value, When, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.template.loader import get_template
from xhtml2pdf import pisa
import pandas as pd
from django.urls import reverse
from .utils import paginate_queryset
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import never_cache
from django.utils.timezone import localdate, make_aware
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


#=========================================== admin dashboard ===========================================================================================================================


@admin_required
@never_cache
def dashboard(request):
    product_count = Product.objects.count()
    cat_count = Category.objects.count()
    usr_count = User.objects.count()
    order_count = CartOrder.objects.count()

    # Calculate total revenue from delivered orders
    delivered_orders = CartOrder.objects.filter(status='Delivered')
    total_revenue = delivered_orders.aggregate(total=Sum('order_total'))['total'] or 0

    # Paginate the orders
    orders_list = CartOrder.objects.all().order_by('-id')
    paginator = Paginator(orders_list, 10)  # Show 10 orders per page

    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    context = {
        'title': 'Admin Dashboard',
        'usr_count': usr_count,
        'order_count': order_count,
        'orders': orders_list,
        'product_count': product_count,
        'cat_count': cat_count,
        'total_revenue': total_revenue,
    }
    return render(request, 'cust_admin/index.html', context)


#=========================================== admin list, view, delete user =========================================================================================================


@admin_required
def user_list(request):
    users = User.objects.all().order_by('id')
    page_obj, paginator = paginate_queryset(request, users, items_per_page=20)  # Adjust items_per_page as needed

    context={
        'title':'User List',
         'users': users,
         'page_obj': page_obj,
         'paginator': paginator
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
    sweetify.toast(request, f"The user {user.username} has been {action} successfully.", icon='success', timer=3000)
    return redirect('cust_admin:user_list')


#=========================================== admin add, list, edit, delete category=========================================================================================================


@admin_required
def category_list(request):
    categories = Category.objects.all().order_by('c_id')
    page_obj, paginator = paginate_queryset(request, categories, items_per_page=20)  # Adjust items_per_page as needed

    context = {
        'title':'Category List',
        'categories':categories,
        'page_obj': page_obj,
        'paginator': paginator,

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
            sweetify.toast(request, f"Category {c_name} with this name already exists.", icon='error', timer=3000)
        else:
            # Create and save the new category
            c_data = Category(c_name=c_name, c_image=c_image)
            c_data.save()
            sweetify.toast(request, "Category added successfully.", icon='success', timer=3000)
            return redirect('cust_admin:category_list')

    return render(request, 'cust_admin/category/add_category.html', context)


@admin_required
def category_list_unlist(request, c_id):
    category = get_object_or_404(Category, c_id = c_id)
    category.is_blocked = not category.is_blocked    
    category.save()
    action = 'unblocked' if not category.is_blocked else 'blocked'
    sweetify.toast(request, f"The category with ID {category.c_id} has been {action} successfully.", icon='success', timer=3000)
    return redirect('cust_admin:category_list')


@admin_required
def edit_category(request, c_id):
    category = get_object_or_404(Category, c_id=c_id)
    
    if request.method == 'POST':
        category.c_name = request.POST.get('cname')
        if request.FILES.get('image'):  # Only update the image if a new one is uploaded
            category.c_image = request.FILES.get('image')
        # Save the updated category
        category.save()
        return redirect('cust_admin:category_list')

    # Pass the category data to the template to prefill the form
    context = {
        'title': 'Edit Category',
        'category': category,
    }
          
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


#=========================================== admin add, list, edit, delete variant =========================================================================================================


@admin_required
def list_variant(request):
    # Define the custom ordering based on the size values
    custom_ordering = Case(
        When(size='S', then=Value(0)),
        When(size='M', then=Value(1)),
        When(size='L', then=Value(2)),
        When(size='XL', then=Value(3)),
        When(size='XXL', then=Value(4)),
        When(size='XXXL', then=Value(5)),
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


@admin_required
def add_variant(request):
    if request.method == 'POST':
        size = request.POST.get('size')

        try:
            existing_size = Size.objects.filter(size__iexact=size)
            if existing_size:
                sweetify.toast(request, "The size already exists", timer=3000, icon='warning')
            else:
                new_size = Size(size=size)
                new_size.save()
                sweetify.toast(request, f'The size {size} added successfully', icon='success', timer=3000)
        except IntegrityError as e:
            error_message = str(e)
            sweetify.toast(request, f'An error occurred while adding the size: {error_message}', icon='alert', timer=3000)
        
        return redirect('cust_admin:list_variant')
    context = {
            'title': 'Variant Add',
        }
    return render(request, 'cust_admin/variant/variant_add.html', context)


@admin_required
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


#=========================================== admin add, list, edit, delete product =========================================================================================================


@admin_required
def prod_list(request):
    products = Product.objects.all().order_by('-p_id')
    page_obj, paginator = paginate_queryset(request, products, items_per_page=20)
    
    context = {
        'products': products,
        'title': 'Product Lobby',
        'paginator': paginator,
        'page_obj': page_obj
    }
    return render(request, 'cust_admin/product/product_list.html', context)


@admin_required
def add_product(request):
    if request.method == 'POST':
        # Maximum file size in bytes (2MB = 2097152 bytes)
        max_file_size = 2097152

        # Extract data from the form
        title = request.POST.get('title')
        description = request.POST.get('description')
        specifications = request.POST.get('specifications')
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')
        featured = request.POST.get('featured') == 'on'
        popular = request.POST.get('popular') == 'on'
        latest = request.POST.get('latest') == 'on'
        availability = request.POST.get('availability') == 'on'

        # Main product image validation
        image = request.FILES.get('image')
        if image and image.size > max_file_size:
            sweetify.error(request, 'Main product image exceeds the 2MB size limit.')
            return redirect('cust_admin:add_product')

        # Validate additional images size
        images = request.FILES.getlist('images')
        for img in images:
            if img.size > max_file_size:
                sweetify.error(request, 'One or more additional images exceed the 2MB size limit.')
                return redirect('cust_admin:add_product')

        # Get the category and subcategory objects
        category = Category.objects.get(c_id=category_id)
        subcategory = Subcategory.objects.get(sid=subcategory_id)

        # Create the product
        product = Product.objects.create(
            title=title,
            description=description,
            specifications=specifications,
            category=category,
            featured=featured,
            popular=popular,
            latest=latest,
            sub_category=subcategory,
            availability=availability,
            image=image  # Assign the main product image
        )

        # Save additional images
        for img in images:
            ProductImages.objects.create(product=product, images=img)

        sweetify.toast(request, 'Product added successfully!', icon='success', timer=3000)
        return redirect('cust_admin:prod_list')

    # If request method is GET, render the form
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    context = {
        'categories': categories,
        'subcategories': subcategories,
    }

    return render(request, 'cust_admin/product/product_add.html', context)



@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, p_id=product_id)
    additional_images = ProductImages.objects.filter(product=product)
    
    if request.method == 'POST':
        max_file_size = 2097152
        title = request.POST.get('title')
        description = request.POST.get('description')
        specifications = request.POST.get('specifications')
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')
        featured = request.POST.get('featured') == 'on'
        popular = request.POST.get('popular') == 'on'
        latest = request.POST.get('latest') == 'on'
        availability = request.POST.get('availability') == 'on'

        main_image = request.FILES.get('image')
        if main_image and main_image.size > max_file_size:
            sweetify.error(request, 'Main product image exceeds the 2MB size limit.')
            return redirect('cust_admin:edit_product', product_id=product_id)

        additional_images_files = request.FILES.getlist('images')
        for img in additional_images_files:
            if img.size > max_file_size:
                sweetify.error(request, 'One or more additional images exceed the 2MB size limit.')
                return redirect('cust_admin:edit_product', product_id=product_id)

        product.title = title
        product.description = description
        product.specifications = specifications
        product.featured = featured
        product.popular = popular
        product.latest = latest
        product.availability = availability

        product.category = get_object_or_404(Category, c_id=category_id)
        product.sub_category = get_object_or_404(Subcategory, sid=subcategory_id)
        
        if main_image:
            product.image = main_image

        product.save()
        ProductImages.objects.filter(product=product).delete()
        for img in additional_images_files:
            ProductImages.objects.create(product=product, images=img)

        sweetify.toast(request, 'Product updated successfully!', icon='success', timer=3000)
        return redirect('cust_admin:prod_list')

    context = {
        'product': product,
        'additional_images': additional_images,
        'categories': Category.objects.all(),
        'subcategories': Subcategory.objects.all(),
    }
    return render(request, 'cust_admin/product/product_edit.html', context)


@admin_required
def product_list_unlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)  # Use product_id here
    product.is_blocked = not product.is_blocked
    product.save()
    action = 'unblocked' if not product.is_blocked else 'blocked'
    sweetify.toast(request, f"The product with ID {product_id} has been {action} successfully.", icon='success', timer=3000)
    return redirect('cust_admin:prod_list')


@admin_required
def prod_catalogue_list(request):    
    products = ProductAttribute.objects.all().order_by('-id')
    page_obj, paginator = paginate_queryset(request, products, items_per_page=20)
    prods = Product.objects.all()
    
    context = {
        'prods': prods,
        'products': products,
        'title': 'Product Catalogue',
        'page_obj': page_obj,
        'paginator': paginator
    }
    return render(request, 'cust_admin/product/product_catalogue.html', context)


@admin_required
def catalogue_list_unlist(request, pk):
    product = get_object_or_404(ProductAttribute, pk=pk)
    product.is_blocked = not product.is_blocked
    product.save()
    action = 'unblocked' if not product.is_blocked else 'blocked'
    sweetify.toast(request, f"The product variant with ID {product.pk} has been {action} successfully.", timer=3000, icon='success')
    return redirect('cust_admin:prod_catalogue')


#=========================================== admin product variant assign, edit =========================================================================================================


@admin_required
def prod_variant_assign(request):
    form = ProductVariantAssignForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        # Process form data
        product = form.cleaned_data['product']
        size = form.cleaned_data['size']
        price = form.cleaned_data['price']
        old_price = form.cleaned_data['old_price']
        stock = form.cleaned_data['stock']
        in_stock = form.cleaned_data['in_stock']
        status = form.cleaned_data['status']
        
        # Check if size already exists for the product
        existing_size = ProductAttribute.objects.filter(product=product, size=size).exists()
        if existing_size:
            sweetify.toast(request, f"The size {size} already added", icon='warning')
        else:
            # Save the form data to the database
            product_attribute = ProductAttribute.objects.create(
                product=product,
                size=size,
                price=price,
                old_price=old_price,
                stock=stock,
                in_stock=in_stock,
                status=status
            )
            sweetify.toast(request, 'Successfully added Product with variant!', timer=3000, icon='success')
            return redirect('cust_admin:prod_catalogue')

    context = {
        'title': 'Add New Product',
        'form': form,
    }
    return render(request, 'cust_admin/product/prod_variant_assign.html', context)


@admin_required
def prod_variant_edit(request, pk):
    product_attribute = get_object_or_404(ProductAttribute, pk=pk)

    if request.method == 'POST':
        form = ProductVariantAssignForm(request.POST)
        if form.is_valid():
            product_attribute.product = form.cleaned_data['product']
            product_attribute.size = form.cleaned_data['size']
            product_attribute.price = form.cleaned_data['price']
            product_attribute.old_price = form.cleaned_data['old_price']
            product_attribute.stock = form.cleaned_data['stock']
            product_attribute.in_stock = form.cleaned_data['in_stock']
            product_attribute.status = form.cleaned_data['status']
            product_attribute.save()
            
            sweetify.toast(request, 'Product attribute details updated successfully!', icon='success', timer=3000)
            return redirect('cust_admin:prod_catalogue')
    else:
        initial_data = {
            'product': product_attribute.product,
            'size': product_attribute.size,
            'price': product_attribute.price,
            'old_price': product_attribute.old_price,
            'stock': product_attribute.stock,
            'in_stock': product_attribute.in_stock,
            'status': product_attribute.status
        }
        form = ProductVariantAssignForm(initial_data=initial_data)

    context = {
        'form': form,
        'title': 'Product Variant Edit',
    }

    return render(request, 'cust_admin/product/prod_variant_edit.html', context)
    

#=========================================== admin list, detail, status update of orders =========================================================================================================


@admin_required
def list_order(request):
    orders = CartOrder.objects.all().order_by('-id')
    page_obj, paginator = paginate_queryset(request, orders, items_per_page=20)  # Adjust items_per_page as needed

    context = {
        'title': 'Order List',
        'orders': page_obj,
        'paginator': paginator,
        'page_obj': page_obj,
    }
    return render(request, 'cust_admin/order/order_list.html', context)


@admin_required
def order_detail(request, order_id):
    order = get_object_or_404(CartOrder, id=order_id)
    items = ProductOrder.objects.filter(order=order)
    product_images = []
    sub_total = 0  # Initialize sub_total here
    print('order=',order.payment_method)
    for item in items:
        product = item.product
        price = item.product_price
        quantity = item.quantity
        total_price = price * quantity  # Calculate total price for current item
        sub_total += total_price  # Increment sub_total with each iteration
        product_images.append({
            'product': item.product,
            'image': item.product.image.url
        })
        # Assign total_price to item
        item.sub = total_price

    context = {
        'title': 'Order Detail',
        'order': order,
        'items': items,
        'product_images': product_images,
        'sub_total': sub_total,  # Pass sub_total to the template context
    }
    return render(request, 'cust_admin/order/order_details.html', context)


@require_POST
@csrf_exempt
def order_update_status(request, order_id):
    order = get_object_or_404(CartOrder, id=order_id)
    status = request.POST.get('status')
    order.status = status
    order.save()

    # Return a JSON response
    return JsonResponse({'success': True, 'message': 'Order status updated successfully.'})


@admin_required
def manage_return_requests(request):
    # Fetch orders with the 'Return Requested' status
    return_requests = CartOrder.objects.filter(status='Return Requested')
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')
        
        # Fetch the order
        order = get_object_or_404(CartOrder, id=order_id)
        
        if action == 'approve':
            if order.status == 'Return Approved':
                messages.error(request, 'This order has already been refunded.')
            else:
                # Approve the return
                order.status = 'Return Approved'
                order.save()
                
                # Process refund to wallet
                wallet, created = Wallet.objects.get_or_create(user=order.user)
                wallet.balance += Decimal(order.order_total)
                wallet.save()
                
                WalletHistory.objects.create(
                    wallet=wallet,
                    transaction_type='Credit',
                    amount=order.order_total,
                    reason='Order Return Approved'
                )
                
                messages.success(request, 'Return request approved and refund processed.')
                
        elif action == 'reject':
            # Reject the return
            order.status = 'Return Rejected'
            order.save()
            
            messages.success(request, 'Return request rejected.')
        
        return redirect('cust_admin:returned_orders')

    return render(request, 'cust_admin/order/manage_return_requests.html', {'return_requests': return_requests})



#=========================================== admin add, list, edit, delete coupons =========================================================================================================


@admin_required
def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            sweetify.toast(request, 'Coupon added successfully!', icon='success', timer=3000)
            return redirect('cust_admin:coupon_list')
        else:
            # Check if the discount field has errors
            if form.errors.get('discount'):
                sweetify.toast(request, 'Discount must be between 1 and 99 percent.', icon='error', timer=3000)
            else:
                sweetify.toast(request, 'There was an error adding the coupon.', icon='error', timer=3000)
    else:
        form = CouponForm()
    
    return render(request, 'cust_admin/coupon/add_coupon.html', {'form': form})


@admin_required
def edit_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            sweetify.toast(request, 'Coupon updated successfully!', icon='success', timer=3000)
            return redirect('cust_admin:coupon_list')
        else:
            sweetify.error(request, 'There was an error updating the coupon. Please check the form for details.', timer=3000)
    else:
        form = CouponForm(instance=coupon)
    return render(request, 'cust_admin/coupon/edit_coupon.html', {'form': form})


@admin_required
def coupon_list(request):
    coupons = Coupon.objects.all()
    page_obj, paginator = paginate_queryset(request, coupons, items_per_page=20)  # Adjust items_per_page as needed
    
    context = {
        'coupons': coupons,
        'page_obj': page_obj,
        'paginator': paginator
    }
    return render(request, 'cust_admin/coupon/coupon_list.html',context)


@admin_required
def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.delete()
    sweetify.toast(request, 'Coupon deleted successfully!', icon='success', timer=3000)
    return redirect('cust_admin:coupon_list')


#=========================================== admin add, list, edit, delete category offers =========================================================================================================


@admin_required
def category_offer_list(request):
    category_offers = CategoryOffer.objects.all()
    page_obj, paginator = paginate_queryset(request, category_offers, items_per_page=20)  # Adjust items_per_page as needed

    context = {
        'category_offers': category_offers,
        'page_obj': page_obj,
        'paginator': paginator
    }
    return render(request, 'cust_admin/offer/category_offer/list_offer.html', context)


@admin_required
def add_category_offer(request):
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST)
        if form.is_valid():
            category_offer = form.save()
            
            if category_offer.is_active:
                # Apply discount to all variants of products in the selected category
                products = Product.objects.filter(category=form.cleaned_data['category'])
                for product in products:
                    product_attributes = ProductAttribute.objects.filter(product=product)
                    for attribute in product_attributes:
                        attribute.old_price = attribute.price
                        discount = Decimal(category_offer.discount_percentage) / Decimal(100)
                        attribute.price = attribute.price - (attribute.price * discount)
                        attribute.save()

            sweetify.toast(request, 'Category offer added successfully', icon='success', timer=3000)
            return redirect('cust_admin:category_offer_list')
        else:
            sweetify.error(request, 'There was an error adding the Offer.', timer=3000)
    else:
        form = CategoryOfferForm()
    return render(request, 'cust_admin/offer/category_offer/add_offer.html', {'form': form, 'title': 'Add Category Offer'})


@admin_required
def edit_category_offer(request, offer_id):
    offer = CategoryOffer.objects.get(pk=offer_id)
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            sweetify.toast(request, 'Category offer updated successfully.', icon='success', timer=3000)
            return redirect('cust_admin:category_offer_list')
        else:
            sweetify.toast(request, 'There was an error in updating offer', icon='error', timer=3000)
    else:
        form = CategoryOfferForm(instance=offer)
    return render(request, 'cust_admin/offer/category_offer/edit_offer.html', {'form': form, 'title': 'Edit Category Offer'})


@admin_required
def delete_category_offer(request, offer_id):
    offer = CategoryOffer.objects.get(id=offer_id)
    product_attributes = ProductAttribute.objects.filter(product__category=offer.category)
    for attribute in product_attributes:
        attribute.price = attribute.old_price  # Reset the price to the old price before deleting the offer
        attribute.old_price = 0  # Reset old price
        attribute.save()
    offer.delete()
    sweetify.toast(request, 'Category offer deleted successfully.', icon='success', timer=3000)
    return redirect('cust_admin:category_offer_list')


#=========================================== admin add, list, edit, delete product offer =========================================================================================================


@admin_required
def product_offer_list(request):
    product_offers = ProductOffer.objects.all()
    page_obj, paginator = paginate_queryset(request, product_offers, items_per_page=20)  # Adjust items_per_page as needed

    context = {
        'product_offers': product_offers,
        'page_obj': page_obj,
        'paginator': paginator
    }
    return render(request, 'cust_admin/offer/product_offer/list_offer.html', context)


@admin_required
def add_product_offer(request):
    if request.method == 'POST':
        form = ProductOfferForm(request.POST)
        if form.is_valid():
            product_offer = form.save()
            
            if product_offer.is_active:
                # Apply discount to all variants of the selected product
                product_attributes = ProductAttribute.objects.filter(product=form.cleaned_data['product'])
                for attribute in product_attributes:
                    attribute.old_price = attribute.price
                    discount = Decimal(product_offer.discount_percentage) / Decimal(100)
                    attribute.price = attribute.price - (attribute.price * discount)
                    attribute.save()

            sweetify.toast(request, 'Product offer added successfully', icon='success', timer=3000)
            return redirect('cust_admin:product_offer_list')
        else:
                        sweetify.error(request, 'There was an error adding the Offer.', timer=3000)
    else:
        form = ProductOfferForm()
    return render(request, 'cust_admin/offer/product_offer/add_offer.html', {'form': form, 'title': 'Add Product Offer'})


@admin_required
def edit_product_offer(request, offer_id):
    offer = ProductOffer.objects.get(id=offer_id)
    if request.method == "POST":
        form = ProductOfferForm(request.POST, instance=offer)
        if form.is_valid():
            previous_product_attributes = ProductAttribute.objects.filter(product=offer.product)
            for attribute in previous_product_attributes:
                attribute.price = attribute.old_price  # Reset the price to the old price before updating
                attribute.old_price = 0  # Reset old price
                attribute.save()
            
            product_offer = form.save()
            
            if product_offer.is_active:
                product_attributes = ProductAttribute.objects.filter(product=offer.product)
                for attribute in product_attributes:
                    attribute.old_price = attribute.price
                    attribute.price = attribute.price - (attribute.price * (product_offer.discount_percentage / 100))
                    attribute.save()

            sweetify.toast(request, 'Product offer updated successfully.', icon='success', timer=3000)
            return redirect(reverse('cust_admin:product_offer_list'))
        else:
            sweetify.toast(request, 'There was an error in updating offer', icon='error', timer=3000)
    else:
        form = ProductOfferForm(instance=offer)
    return render(request, 'cust_admin/offer/product_offer/edit_offer.html', {'form': form})


@admin_required
def delete_product_offer(request, offer_id):
    offer = ProductOffer.objects.get(id=offer_id)
    product_attributes = ProductAttribute.objects.filter(product=offer.product)
    for attribute in product_attributes:
        attribute.price = attribute.old_price  # Reset the price to the old price before deleting the offer
        attribute.old_price = 0  # Reset old price
        attribute.save()
    offer.delete()
    sweetify.toast(request, 'Product offer deleted successfully.', icon='success', timer=3000)
    return redirect(reverse('cust_admin:product_offer_list'))


#=========================================== sales, weekly, daily, monthly reports =========================================================================================================


@admin_required
def sales_report(request):
    start_date_value = ""
    end_date_value = ""
    orders = CartOrder.objects.filter(status='Delivered')

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_date_value = start_date
        end_date_value = end_date

        print(f"Received Start Date: {start_date}")
        print(f"Received End Date: {end_date}")

        if start_date and end_date:
            try:
                start_date = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
                end_date = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

                print(f"Processed Start Date: {start_date}")
                print(f"Processed End Date: {end_date}")

                orders = CartOrder.objects.filter(
                    created_at__range=(start_date, end_date),
                    status='Delivered'
                ).order_by('created_at')

            except ValueError as e:
                print(f"Date parsing error: {e}")

        if 'export_pdf' in request.POST:
            request.session['filtered_orders'] = list(orders.values())
            request.session['start_date'] = start_date.strftime('%Y-%m-%d')
            request.session['end_date'] = end_date.strftime('%Y-%m-%d')
            return redirect('export_pdf', report_type='custom')
        elif 'export_excel' in request.POST:
            request.session['filtered_orders'] = list(orders.values())
            request.session['start_date'] = start_date.strftime('%Y-%m-%d')
            request.session['end_date'] = end_date.strftime('%Y-%m-%d')
            return redirect('export_excel', report_type='custom')

    # Calculate total orders and total sum
    total_count = orders.count()
    total_sum = orders.aggregate(total_sum=Sum('order_total'))['total_sum']

    context = {
        'orders': orders,
        'start_date_value': start_date_value,
        'end_date_value': end_date_value,
        'current_date': timezone.now().date(),
        'total_count': total_count,
        'total_sum': total_sum,
    }

    return render(request, 'cust_admin/statistics/sales_report.html', context)


@admin_required
def export_to_pdf(request, report_type, orders=None, start_date=None, end_date=None):
    template_path = 'cust_admin/statistics/pdf_template.html'
    context = {}

    total_sum = 0
    total_count = 0

    # Debugging statements
    print(f"Report Type: {report_type}, Start Date: {start_date}, End Date: {end_date}")

    if report_type == 'custom' and orders is not None:
        print(f"Orders count before summing: {orders.count()}")
        print(f"Orders fetched: {list(orders)}")

        context['orders'] = orders
        context['start_date'] = start_date
        context['end_date'] = end_date
        total_sum = orders.aggregate(Sum('order_total'))['order_total__sum'] or 0
        total_count = orders.count()
    elif report_type == 'daily':
        today = timezone.localdate()
        daily_orders = CartOrder.objects.filter(created_at__date=today, status='Delivered')
        print(f"Daily Orders fetched: {list(daily_orders)}")
        total_sum = daily_orders.aggregate(Sum('order_total'))['order_total__sum'] or 0
        total_count = daily_orders.count()
        context['orders'] = daily_orders
    elif report_type == 'weekly':
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        weekly_orders = CartOrder.objects.filter(created_at__range=(start_of_week, end_of_week), status='Delivered')
        print(f"Weekly Orders fetched: {list(weekly_orders)}")
        total_sum = weekly_orders.aggregate(Sum('order_total'))['order_total__sum'] or 0
        total_count = weekly_orders.count()
        context['orders'] = weekly_orders
    elif report_type == 'monthly':
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - timedelta(days=1))
        monthly_orders = CartOrder.objects.filter(created_at__range=(start_of_month, end_of_month), status='Delivered')
        print(f"Monthly Orders fetched: {list(monthly_orders)}")
        total_sum = monthly_orders.aggregate(Sum('order_total'))['order_total__sum'] or 0
        total_count = monthly_orders.count()
        context['orders'] = monthly_orders

    context['total_sum'] = total_sum
    context['total_count'] = total_count

    # Debugging statements
    print(f"Context for PDF after filtering: {context}")

    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
    

@admin_required    
def export_to_excel(request, report_type, orders=None, start_date=None, end_date=None):
    if report_type == 'custom' and orders is not None:
        pass  # orders are already filtered
    elif report_type == 'daily':
        today = timezone.localdate()
        orders = CartOrder.objects.filter(created_at__date=today, status='Delivered')
    elif report_type == 'weekly':
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        orders = CartOrder.objects.filter(created_at__range=(start_of_week, end_of_week), status='Delivered')
    elif report_type == 'monthly':
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - timedelta(days=1))
        orders = CartOrder.objects.filter(created_at__range=(start_of_month, end_of_month), status='Delivered')
    
    # Convert QuerySet to DataFrame
    data = {
        'Order Number': [order.order_number for order in orders],
        'User': [order.user.username for order in orders],
        'Total': [order.order_total for order in orders],
        'Status': [order.status for order in orders],
    }
    df = pd.DataFrame(data)
    
    # Add aggregate rows
    df.loc['Total'] = ['Total', '', df['Total'].sum(), '']
    df.loc['Count'] = ['Count', '', len(orders), '']
    
    # Create Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xlsx"'
    df.to_excel(response, index=False)
    
    return response


@admin_required
def daily_report(request):
    today = timezone.localdate()
    daily_orders = CartOrder.objects.filter(created_at__date=today, status='Delivered')
    context = {'daily_orders': daily_orders}
    return render(request, 'cust_admin/statistics/daily_report.html', context)


@admin_required
def weekly_report(request):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    weekly_orders = CartOrder.objects.filter(created_at__range=(start_of_week, end_of_week), status='Delivered')
    context = {'weekly_orders': weekly_orders}
    return render(request, 'cust_admin/statistics/weekly_report.html', context)


@admin_required
def monthly_report(request):
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - timedelta(days=1))
    monthly_orders = CartOrder.objects.filter(created_at__range=(start_of_month, end_of_month), status='Delivered')
    context = {'monthly_orders': monthly_orders}
    return render(request, 'cust_admin/statistics/monthly_report.html', context)


#=========================================== admin home bar and pie graphs =========================================================================================================


@admin_required
def sales_statistics(request):
    # Get the count of delivered products per day for the last 7 days
    today = timezone.now().date()
    start_date = today - timedelta(days=6)

    daily_sales = (
        CartOrder.objects.filter(created_at__date__range=[start_date, today], status='Delivered')
        .extra(select={'day': 'date(created_at)'})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    # Format the data for Chart.js
    labels = [day['day'].strftime('%Y-%m-%d') for day in daily_sales]
    data = [day['count'] for day in daily_sales]

    return JsonResponse({'labels': labels, 'data': data})


@admin_required
def get_daily_sales_data(request):
    today = timezone.localdate()
    daily_orders = (
        CartOrder.objects.filter(created_at__date=today, status='Delivered')
        .extra(select={'hour': 'strftime("%%H", created_at)'})
        .values('hour')
        .annotate(count=Count('id'))
        .order_by('hour')
    )

    labels = [f"{int(hour['hour']):02d}:00" for hour in daily_orders]
    data = [hour['count'] for hour in daily_orders]

    return JsonResponse({'labels': labels, 'data': data})


@admin_required
def get_monthly_sales_data(request):
    today = timezone.localdate()
    start_of_month = today.replace(day=1)
    end_of_month = today.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1)
    monthly_orders = (
        CartOrder.objects.filter(created_at__date__range=[start_of_month, end_of_month], status='Delivered')
        .extra(select={'day': 'date(created_at)'})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    labels = [day['day'].strftime('%Y-%m-%d') for day in monthly_orders]
    data = [day['count'] for day in monthly_orders]

    return JsonResponse({'labels': labels, 'data': data})


@admin_required
def get_yearly_sales_data(request):
    today = timezone.localdate()
    start_of_year = today.replace(month=1, day=1)
    yearly_orders = (
        CartOrder.objects.filter(created_at__date__range=[start_of_year, today], status='Delivered')
        .extra(select={'month': 'strftime("%%m", created_at)'})
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    labels = [f"{int(month['month']):02d}" for month in yearly_orders]
    data = [month['count'] for month in yearly_orders]

    return JsonResponse({'labels': labels, 'data': data})


@admin_required
def get_order_status_data(request):
    order_status_counts = (
        CartOrder.objects.values('status')
        .annotate(count=Count('id'))
        .order_by('status')
    )

    labels = [status['status'] for status in order_status_counts]
    data = [status['count'] for status in order_status_counts]

    return JsonResponse({'labels': labels, 'data': data})


#=========================================== Best Selling Details =========================================================================================================================================


@admin_required
def format_quantities(product_quantities):
    size_labels = {
        1: 'S',
        2: 'M',
        3: 'L',
        4: 'XL',
        6: 'XXL',
        7: 'XXXL',
        10: 'XXXXL'
    }

    formatted_quantities = []
    
    for product in Product.objects.filter(p_id__in=product_quantities.keys()):
        quantities = product_quantities[product.p_id]
        formatted_quantities.append({
            'product': product,
            'quantities': f"Total Quantity Sold: {quantities}"
        })
        
    return formatted_quantities


@admin_required
def best_selling_products(request):
    # Get top-selling products based on quantity
    best_selling_products = ProductOrder.objects.values('product').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:10]
    product_ids = [item['product'] for item in best_selling_products]
    top_products = Product.objects.filter(p_id__in=product_ids)

    # Map product IDs to their quantities
    product_quantities = {item['product']: item['total_quantity'] for item in best_selling_products}

    # Format quantities into a human-readable form
    formatted_quantities = format_quantities(product_quantities)

    # Count of top products
    product_count = top_products.count()

    context = {
        'title': 'Top Best  Selling',
        'top_products': top_products,
        'product_quantities': formatted_quantities,
        'product_count': product_count,  # Pass product count to the context
    }
    return render(request, 'cust_admin/best_selling_products.html', context)



