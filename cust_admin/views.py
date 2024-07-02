from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from accounts.models import User
from cust_auth_admin.views import admin_required
from store.models import *
from django.http import HttpResponseBadRequest, HttpResponse
from cust_admin.forms import ProductVariantAssignForm, CouponForm, CategoryOfferForm, ProductOfferForm
from django.contrib import messages
from decimal import Decimal
import sweetify
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import IntegrityError
from PIL import Image
from django.db.models import Case, CharField, Value, When
from django.utils import timezone
from datetime import datetime, timedelta
from django.template.loader import get_template
from xhtml2pdf import pisa
import pandas as pd
from django.urls import reverse

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

#=========================================== admin add, list, edit, delete variant =========================================================================================================

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
                messages.success(request, f'The size {size} added successfully')
        except IntegrityError as e:
            error_message = str(e)
            sweetify.toast(request, f'An error occurred while adding the size: {error_message}', icon='alert', timer=3000)
        
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

#=========================================== admin add, list, edit, delete product =========================================================================================================

@admin_required
def prod_list(request):
    products = Product.objects.all().order_by('p_id')
    
    context = {
        'products': products,
        'title': 'Product Lobby',
    }
    return render(request, 'cust_admin/product/product_list.html', context)

@admin_required
def add_product(request):
    if request.method == 'POST':
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
        # Main product image
        image = request.FILES.get('image')

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
        images = request.FILES.getlist('images')  # Additional product images
        for img in images:
            ProductImages.objects.create(product=product, images=img)

        messages.success(request, 'Product added successfully!')
        return redirect('cust_admin:prod_list')
    
    # If request method is GET, render the form
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    context = {
        'categories': categories,
        'subcategories': subcategories,
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
        specifications = request.POST.get('specifications', product.specifications)
        product.category_id = request.POST.get('category', product.category)
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

            messages.success(request, 'Product attribute details updated successfully!')
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
        form = ProductVariantAssignForm(initial=initial_data)

    context = {
        'form': form,
        'title': 'Product Variant Edit',
    }

    return render(request, 'cust_admin/product/prod_variant_edit.html', context)



def prod_catalogue_list(request):    
    products = ProductAttribute.objects.all().order_by('product')
    prods = Product.objects.all()
    
    context = {
        'prods': prods,
        'products': products,
        'title': 'Product Catalogue',
    }
    return render(request, 'cust_admin/product/product_catalogue.html', context)

def catalogue_list_unlist(request, pk):
    product = get_object_or_404(ProductAttribute, pk=pk)
    product.is_blocked = not product.is_blocked
    product.save()
    action = 'unblocked' if not product.is_blocked else 'blocked'
    sweetify.toast(request, f"The product variant with ID {product.pk} has been {action} successfully.", timer=3000, icon='success')
    return redirect('cust_admin:prod_catalogue')

def list_order(request):
    orders = CartOrder.objects.all().order_by('id')
    context = {
        'title': 'Order List',
        'orders': orders,
    }
    return render(request, 'cust_admin/order/order_list.html', context)

def order_detail(request, order_id):
    order = get_object_or_404(CartOrder, id=order_id)
    items = ProductOrder.objects.filter(order=order)
    product_images = []
    sub_total = 0  # Initialize sub_total here
    
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
    return render(request, 'cust_admin/order/order_dtls.html', context)




def order_update_status(request, order_id):
    order = get_object_or_404(CartOrder, id=order_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        order.status = status
        order.save()
        messages.success(request, 'Order status updated successfully.')
        return redirect('cust_admin:list_order')
    context = {
        'title': 'Update Order Status',
        'order': order,
    }
    return render(request, 'cust_admin/order/order_update_status.html', context)


def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            sweetify.toast(request, 'Coupon added successfully!', icon='success', timer=3000)
            return redirect('cust_admin:coupon_list')
        else:
            sweetify.error(request, 'There was an error adding the coupon.', timer=3000)
    else:
        form = CouponForm()
    
    return render(request, 'cust_admin/coupon/add_coupon.html', {'form': form})

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

def coupon_list(request):
    coupons = Coupon.objects.all()
    return render(request, 'cust_admin/coupon/coupon_list.html', {'coupons': coupons})

def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.delete()
    sweetify.toast(request, 'Coupon deleted successfully!', icon='success', timer=3000)
    return redirect('cust_admin:coupon_list')

def category_offer_list(request):
    category_offers = CategoryOffer.objects.all()
    return render(request, 'cust_admin/offer/category_offer/list_offer.html', {'category_offers': category_offers})

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
            error_message = " ".join([str(error) for error in form.errors.get('__all__', [])])
            sweetify.toast(request, error_message, icon='error', timer=3000)
    else:
        form = CategoryOfferForm()
    return render(request, 'cust_admin/offer/category_offer/add_offer.html', {'form': form, 'title': 'Add Category Offer'})

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

def delete_category_offer(request, offer_id):
    offer = CategoryOffer.objects.get(pk=offer_id)
    offer.delete()
    sweetify.toast(request, 'Category offer deleted successfully.', icon='success', timer=3000)
    return redirect('cust_admin:category_offer_list')

def product_offer_list(request):
    product_offers = ProductOffer.objects.all()
    return render(request, 'cust_admin/offer/product_offer/list_offer.html', {'product_offers': product_offers})

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
            error_message = " ".join([str(error) for error in form.errors.get('__all__', [])])
            sweetify.toast(request, error_message, icon='error', timer=3000)
    else:
        form = ProductOfferForm()
    return render(request, 'cust_admin/offer/product_offer/add_offer.html', {'form': form, 'title': 'Add Product Offer'})

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




def sales_report(request):
    start_date_value = ""
    end_date_value = ""
    orders = CartOrder.objects.filter(status='Delivered')  # Use your appropriate status

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_date_value = start_date
        end_date_value = end_date

        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            orders = CartOrder.objects.filter(created_at__range=(start_date, end_date), status='Delivered').order_by('created_at')

    context = {
        'orders': orders,
        'start_date_value': start_date_value,
        'end_date_value': end_date_value,
    }

    return render(request, 'cust_admin/statistics/sales_report.html', context)



############################################################################################################################################################################################################################


def daily_report(request):
    today = timezone.localdate()
    daily_orders = CartOrder.objects.filter(created_at__date=today, status='Delivered')
    context = {'daily_orders': daily_orders}
    return render(request, 'cust_admin/statistics/daily_report.html', context)

def weekly_report(request):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    weekly_orders = CartOrder.objects.filter(created_at__range=(start_of_week, end_of_week), status='Delivered')
    context = {'weekly_orders': weekly_orders}
    return render(request, 'cust_admin/statistics/weekly_report.html', context)

def monthly_report(request):
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - timedelta(days=1))
    monthly_orders = CartOrder.objects.filter(created_at__range=(start_of_month, end_of_month), status='Delivered')
    context = {'monthly_orders': monthly_orders}
    return render(request, 'cust_admin/statistics/monthly_report.html', context)

def export_to_pdf(request, report_type):
    template_path = 'cust_admin/statistics/pdf_template.html'
    context = {}
    
    if report_type == 'daily':
        today = timezone.now().date()
        daily_orders = CartOrder.objects.filter(created_at__date=today, status='Delivered')
        context['orders'] = daily_orders
    elif report_type == 'weekly':
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        weekly_orders = CartOrder.objects.filter(created_at__range=(start_of_week, end_of_week), status='Delivered')
        context['orders'] = weekly_orders
    elif report_type == 'monthly':
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - timedelta(days=1))
        monthly_orders = CartOrder.objects.filter(created_at__range=(start_of_month, end_of_month), status='Delivered')
        context['orders'] = monthly_orders
    
    # Rendered template
    template = get_template(template_path)
    html = template.render(context)
    
    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # Return PDF file
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def export_to_excel(request, report_type):
    if report_type == 'daily':
        today = timezone.now().date()
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
    
    # Create Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xlsx"'
    df.to_excel(response, index=False)
    
    return response
