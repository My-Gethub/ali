from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from .models import Car, Category, BlogPost, Accessory, ContactMessage, CarOrder, Order, CarInquiry, Notification, Wishlist, Profile
from django.contrib import messages
from .forms import CarForm, AccessoryForm, CarInquiryForm, CarReviewForm, UserUpdateForm, AdminUserUpdateForm, AdminUserCreationForm
from django.db.models import Q

from django.shortcuts import render
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt

@xframe_options_exempt
def view1(request):
    from django.http import HttpResponse
    return HttpResponse("This page is safe to load in a frame on any site.")

@csrf_exempt
def myview(request):
    # هذه الدالة الآن غير محمية من هجمات CSRF لأغراض الاختبار
    from django.http import HttpResponse
    return HttpResponse("CSRF Exempt View for Testing")

def index(request):
    # Retrieve and print the CSRF token for debugging/security monitoring
    token = get_token(request)
    print(f"CSRF Token: {token}")
    
    cars = Car.objects.all().order_by('-created_at')
    
    # Get all categories for filter
    categories = Category.objects.all()
    
    # Get model years for filter (distinct)
    model_years = Car.objects.order_by('-model_year').values_list('model_year', flat=True).distinct()

    context = {
        'cars': cars,
        'deals': cars.filter(status='Used')[:5],
        'categories': categories,
        'model_years': model_years,
        'STATUS_CHOICES': Car.STATUS_CHOICES,
    }
    return render(request, 'index.html', context)

def search(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    status = request.GET.get('status')
    model_year = request.GET.get('model_year')
    
    cars = Car.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    selected_category = None

    if query:
        cars = cars.filter(Q(title__icontains=query) | Q(description__icontains=query))
    
    if category_id and category_id.strip():
        try:
            selected_category = Category.objects.get(id=category_id)
            cars = cars.filter(category=selected_category)
        except (Category.DoesNotExist, ValueError):
            pass
        
    if status and status.strip():
        # status should match STATUS_CHOICES exactly ('New' or 'Used')
        cars = cars.filter(status__iexact=status.strip())
        
    if model_year and model_year.strip():
        try:
            cars = cars.filter(model_year=int(model_year.strip()))
        except ValueError:
            pass

    context = {
        'cars': cars,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
        'selected_status': status,
        'selected_year': model_year,
        'active_page': 'all_cars',
        'is_search': True,
        'results_count': cars.count()
    }
    # Reuse inventory template for results
    return render(request, 'car-inventory.html', context)

def car_detail(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    reviews = car.reviews.all().order_by('-created_at')
    
    inquiry_form = CarInquiryForm()
    review_form = CarReviewForm()

    if request.method == 'POST':
        if 'submit_inquiry' in request.POST:
            inquiry_form = CarInquiryForm(request.POST)
            if inquiry_form.is_valid():
                inquiry = inquiry_form.save(commit=False)
                inquiry.car = car
                if request.user.is_authenticated:
                    inquiry.user = request.user
                inquiry.save()
                messages.success(request, 'Your inquiry has been sent to the seller!')
                return redirect('car_detail', car_id=car_id)
        
        elif 'submit_review' in request.POST and request.user.is_authenticated:
            review_form = CarReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.car = car
                review.user = request.user
                review.save()
                messages.success(request, 'Your review has been submitted!')
                return redirect('car_detail', car_id=car_id)

    # Pre-fill inquiry form if user is logged in
    initial_data = {}
    if request.user.is_authenticated:
        initial_data = {
            'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'email': request.user.email
        }
        inquiry_form = CarInquiryForm(initial=initial_data)

    return render(request, 'car-detail.html', {
        'car': car, 
        'inquiry_form': inquiry_form,
        'reviews': reviews,
        'review_form': review_form
    })

@login_required
def car_create(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.seller = request.user
            car.save()
            return redirect('car_detail', car_id=car.id)
    else:
        form = CarForm()
    return render(request, 'car_form.html', {'form': form})

@login_required
def car_update(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    # Allow if user is seller OR superuser
    if car.seller != request.user and not request.user.is_superuser:
        return redirect('car_detail', car_id=car.id) # Or 403 Forbidden
        
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            return redirect('car_detail', car_id=car.id)
    else:
        form = CarForm(instance=car)
    return render(request, 'car_form.html', {'form': form})

@login_required
def car_delete(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    # Allow if user is seller OR superuser
    if car.seller != request.user and not request.user.is_superuser:
         return redirect('car_detail', car_id=car.id)
         
    if request.method == 'POST':
        car.delete()
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('index')
    return render(request, 'car_confirm_delete.html', {'car': car})

@login_required
def accessory_create(request):
    if request.method == 'POST':
        form = AccessoryForm(request.POST, request.FILES)
        if form.is_valid():
            accessory = form.save(commit=False)
            accessory.seller = request.user
            accessory.save()
            return redirect('accessory_detail', accessory_id=accessory.id)
    else:
        form = AccessoryForm()
    return render(request, 'accessory_form.html', {'form': form})

@login_required
def accessory_update(request, pk):
    accessory = get_object_or_404(Accessory, pk=pk)
    # Allow if user is seller OR superuser
    if accessory.seller != request.user and not request.user.is_superuser:
        return redirect('accessory_detail', accessory_id=accessory.id)
        
    if request.method == 'POST':
        form = AccessoryForm(request.POST, request.FILES, instance=accessory)
        if form.is_valid():
            form.save()
            return redirect('accessory_detail', accessory_id=accessory.id)
    else:
        form = AccessoryForm(instance=accessory)
    return render(request, 'accessory_form.html', {'form': form})

@login_required
def accessory_delete(request, pk):
    accessory = get_object_or_404(Accessory, pk=pk)
    # Allow if user is seller OR superuser
    if accessory.seller != request.user and not request.user.is_superuser:
         return redirect('accessory_detail', accessory_id=accessory.id)
         
    if request.method == 'POST':
        accessory.delete()
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('grid')
    return render(request, 'accessory_confirm_delete.html', {'accessory': accessory})

from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required

def admin_dashboard(request):
    """Custom admin dashboard"""
    if not request.user.is_authenticated:
        raise Http404("Page not found")
        
    if not request.user.is_staff:
        return redirect('dashboard')

    # Stats
    total_users = User.objects.count()
    total_cars = Car.objects.count()
    total_accessories = Accessory.objects.count()
    total_orders = Order.objects.count() + CarOrder.objects.count()
    
    # Recent items
    recent_cars = Car.objects.all().order_by('-created_at')[:10]
    recent_accessories = Accessory.objects.all().order_by('-created_at')[:10]
    recent_users = User.objects.all().order_by('-date_joined')[:10]
    
    # Full lists for management
    all_categories = Category.objects.all()
    all_posts = BlogPost.objects.all().order_by('-created_at')
    
    # Extra admin lists
    all_car_orders = CarOrder.objects.all().order_by('-created_at')
    all_accessory_orders = Order.objects.all().order_by('-created_at')
    all_inquiries = CarInquiry.objects.all().order_by('-created_at')
    all_reviews = CarReview.objects.all().order_by('-created_at')
    all_messages = ContactMessage.objects.all().order_by('-created_at')
    
    context = {
        'total_users': total_users,
        'total_cars': total_cars,
        'total_accessories': total_accessories,
        'total_orders': total_orders,
        'recent_cars': recent_cars,
        'recent_accessories': recent_accessories,
        'recent_users': recent_users,
        'all_categories': all_categories,
        'all_posts': all_posts,
        'all_car_orders': all_car_orders,
        'all_accessory_orders': all_accessory_orders,
        'all_inquiries': all_inquiries,
        'all_reviews': all_reviews,
        'all_messages': all_messages,
    }
    return render(request, 'admin_dashboard.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def dashboard(request):
    # Items the user is selling
    cars = Car.objects.filter(seller=request.user).order_by('-created_at')
    accessories = Accessory.objects.filter(seller=request.user).order_by('-created_at')
    
    # Orders RECEIVED for the user's cars
    received_car_orders = CarOrder.objects.filter(car__seller=request.user).order_by('-created_at')
    
    # Orders RECEIVED for the user's accessories
    received_accessory_orders = Order.objects.filter(items__accessory__seller=request.user).distinct().order_by('-created_at')
    
    # Inquiries RECEIVED for the user's cars
    received_inquiries = CarInquiry.objects.filter(car__seller=request.user).order_by('-created_at')
    
    # Orders PLACED by the user (as a customer)
    my_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # If superuser, show all accessory orders on the platform
    platform_accessory_orders = None
    if request.user.is_superuser:
        platform_accessory_orders = Order.objects.all().order_by('-created_at')
        
    # Notifications for the current user
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # --- ADMIN SUPERUSER EXTRAS ---
    admin_context = {}
    if request.user.is_superuser:
        admin_context = {
            'all_categories': Category.objects.all(),
            'all_posts': BlogPost.objects.all().order_by('-created_at'),
            'all_users': User.objects.all().order_by('-date_joined'),
        }

    context = {
        'cars': cars,
        'accessories': accessories,
        'received_car_orders': received_car_orders,
        'received_accessory_orders': received_accessory_orders,
        'received_inquiries': received_inquiries,
        'orders': my_orders,
        'platform_accessory_orders': platform_accessory_orders,
        'notifications': notifications,
        **admin_context
    }
    return render(request, 'dashboard.html', context)

# --- CATEGORY MANAGEMENT ---
from .forms import CategoryForm

@staff_member_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('admin_dashboard')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})

@staff_member_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category_form.html', {'form': form})

@staff_member_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'category_confirm_delete.html', {'category': category})

# --- BLOG MANAGEMENT ---
from .forms import BlogPostForm

@staff_member_required
def blog_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Blog post created successfully!')
            return redirect('admin_dashboard')
    else:
        form = BlogPostForm()
    return render(request, 'blog_form.html', {'form': form})

@staff_member_required
def blog_update(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'blog_form.html', {'form': form})

@staff_member_required
def blog_delete(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Blog post deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'blog_confirm_delete.html', {'post': post})

# --- USER MANAGEMENT ---

@staff_member_required
def user_delete(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    if user_obj.is_superuser:
        messages.error(request, 'Cannot delete a superuser!')
        return redirect('admin_dashboard')
        
    if request.method == 'POST':
        user_obj.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'user_confirm_delete.html', {'user_obj': user_obj})

@staff_member_required
def toggle_staff_status(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    if user_obj.is_superuser:
        messages.error(request, 'Cannot change status of a superuser!')
        return redirect('admin_dashboard')
        
    user_obj.is_staff = not user_obj.is_staff
    user_obj.save()
    status = "Staff" if user_obj.is_staff else "Regular User"
    messages.success(request, f'User {user_obj.username} is now a {status}.')
    return redirect('admin_dashboard')

@staff_member_required
def admin_user_edit(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    # Prevent editing superusers unless you are a superuser yourself? 
    # Actually Django admin allows superusers to edit each other. 
    # But usually we want to protect the main admin from being messed with if there are other staff members.
    
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"User {user_obj.username} updated successfully!")
            return redirect('admin_dashboard')
    else:
        form = AdminUserUpdateForm(instance=user_obj)
    
    return render(request, 'admin_user_form.html', {'form': form, 'user_obj': user_obj})

@staff_member_required
def admin_user_create(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User {user.username} created successfully!")
            return redirect('admin_dashboard')
    else:
        form = AdminUserCreationForm()
    
    return render(request, 'admin_user_form.html', {'form': form, 'title': 'Create User'})

@login_required
def approve_car_order(request, order_id):
    order = get_object_or_404(CarOrder, id=order_id, car__seller=request.user)
    order.status = 'Approved'
    order.save()
    Notification.objects.create(
        user=order.user,
        message=f"Your order for '{order.car.title}' has been approved! Please contact the seller to proceed."
    )
    return redirect('dashboard')

@login_required
def decline_car_order(request, order_id):
    order = get_object_or_404(CarOrder, id=order_id, car__seller=request.user)
    order.status = 'Declined'
    order.save()
    Notification.objects.create(
        user=order.user,
        message=f"We're sorry, your order for '{order.car.title}' has been declined."
    )
    return redirect('dashboard')

@login_required
def approve_accessory_order(request, order_id):
    # An accessory order can contain items from multiple sellers.
    # We find items belonging to this seller.
    order = get_object_or_404(Order, id=order_id)
    # Check if seller has items in this order
    seller_items = order.items.filter(accessory__seller=request.user)
    if not seller_items.exists():
         return redirect('dashboard')

    order.status = 'Approved'
    order.save()
    Notification.objects.create(
        user=order.user,
        message=f"Your accessory order #{order.id} has been approved by the seller!"
    )
    return redirect('dashboard')

@login_required
def decline_accessory_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    seller_items = order.items.filter(accessory__seller=request.user)
    if not seller_items.exists():
         return redirect('dashboard')
         
    order.status = 'Declined'
    order.save()
    Notification.objects.create(
        user=order.user,
        message=f"Your accessory order #{order.id} has been declined."
    )
    return redirect('dashboard')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        # Handle profile update manualy for now since we don't have a ProfileForm (or create one on the fly)
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        
        if user_form.is_valid():
            user_form.save()
            
            # Update Profile
            if hasattr(request.user, 'profile'):
                profile = request.user.profile
                profile.phone = phone
                profile.address = address
                profile.city = city
                profile.save()
                
            messages.success(request, 'Your profile has been updated!')
            return redirect('dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
    
    return render(request, 'edit_profile.html', {'form': user_form})

def about_us(request):
    return render(request, 'about-us.html')

def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject', '') # Subject might be optional or hidden
        comment = request.POST.get('comment')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=comment
        )
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact_us')
    return render(request, 'contact-us.html')

def blog(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'blog.html', {'posts': posts})

def blog_detail(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    return render(request, 'blog_detail.html', {'post': post})

def grid(request, category_id=None):
    accessories = Accessory.objects.all().order_by('-created_at')
    # Exclude Cars category from accessories sidebar
    categories = Category.objects.exclude(name='Cars')
    selected_category = None
    
    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        accessories = accessories.filter(category=selected_category)
        
    return render(request, 'grid.html', {
        'accessories': accessories,
        'categories': categories,
        'selected_category': selected_category,
        'active_page': 'accessories'
    })

def accessory_detail(request, accessory_id):
    accessory = get_object_or_404(Accessory, id=accessory_id)
    # Get related accessories from the same category
    related_accessories = Accessory.objects.filter(category=accessory.category).exclude(id=accessory_id)[:4]
    
    # If not enough, fill with others
    if related_accessories.count() < 4:
        others = Accessory.objects.exclude(id__in=[accessory.id] + [a.id for a in related_accessories])[:4-related_accessories.count()]
        related_accessories = list(related_accessories) + list(others)
        
    return render(request, 'accessories-detail.html', {
        'accessory': accessory,
        'related_accessories': related_accessories
    })

def car_inventory(request, category_id=None):
    cars = Car.objects.all().order_by('-created_at')
    # Only show Cars category (or empty since cars have single category)
    categories = Category.objects.filter(name='Cars')
    selected_category = None
    
    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        cars = cars.filter(category=selected_category)
    
    return render(request, 'car-inventory.html', {
        'cars': cars,
        'categories': categories,
        'selected_category': selected_category,
        'active_page': 'all_cars'
    })


def user_logout(request):
    logout(request)
    return redirect('index')

def error_404(request, exception=None):
    return render(request, '404error.html', status=404)

def list_cars(request):
    cars = Car.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'list.html', {
        'cars': cars,
        'categories': categories,
        'active_page': 'list_cars'
    })

def list_accessories(request, category_id=None):
    accessories = Accessory.objects.all().order_by('-created_at')
    # Exclude Cars category from accessories sidebar
    categories = Category.objects.exclude(name='Cars')
    selected_category = None
    
    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        accessories = accessories.filter(category=selected_category)
        
    return render(request, 'list1.html', {
        'accessories': accessories,
        'categories': categories,
        'selected_category': selected_category,
        'active_page': 'list_accessories'
    })

def shopping_cart(request):
    if not request.user.is_authenticated:
        return render(request, 'shopping-cart.html', {'active_page': 'cart'})
        
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('update_cart_action')
        
        if action == 'empty_cart':
            cart.items.all().delete()
            messages.success(request, "Shopping cart emptied.")
            
        elif action == 'update_qty':
            for key, value in request.POST.items():
                if key.startswith('cart['):
                    # Extract item ID from key like "cart[123][qty]"
                    try:
                        import re
                        match = re.search(r'cart\[(\d+)\]\[qty\]', key)
                        if match:
                            item_id = match.group(1)
                            qty = int(value)
                            if qty > 0:
                                cart_item = CartItem.objects.get(pk=item_id, cart=cart)
                                cart_item.quantity = qty
                                cart_item.save()
                            else:
                                CartItem.objects.get(pk=item_id, cart=cart).delete()
                    except (ValueError, CartItem.DoesNotExist):
                        continue
            messages.success(request, "Shopping cart updated.")
            
        return redirect('shopping_cart')

    return render(request, 'shopping-cart.html', {'active_page': 'cart', 'cart': cart})

@login_required
def add_to_cart(request, accessory_id):
    accessory = get_object_or_404(Accessory, pk=accessory_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get quantity from request, default to 1
    qty = request.GET.get('qty') or request.POST.get('qty') or 1
    try:
        qty = int(qty)
    except (TypeError, ValueError):
        qty = 1
        
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, accessory=accessory)
    if not item_created:
        cart_item.quantity += qty
    else:
        cart_item.quantity = qty
    cart_item.save()
        
    messages.success(request, f"{qty} x {accessory.title} added to cart.")
    return redirect('shopping_cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('shopping_cart')

from .models import Car, Category, BlogPost, Accessory, Cart, CartItem, Wishlist, CarInquiry, CarReview, CarOrder, Order, OrderItem

def wishlist(request):
    if not request.user.is_authenticated:
        return redirect('login')
    wishlist_obj, created = Wishlist.objects.get_or_create(user=request.user)
    cars = wishlist_obj.cars.all()
    accessories = wishlist_obj.accessories.all()
    return render(request, 'wishlist.html', {
        'active_page': 'wishlist',
        'cars': cars,
        'accessories': accessories
    })

@login_required
def toggle_wishlist(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    wishlist_obj, created = Wishlist.objects.get_or_create(user=request.user)
    
    if car in wishlist_obj.cars.all():
        wishlist_obj.cars.remove(car)
        messages.info(request, f"{car.title} removed from wishlist.")
    else:
        wishlist_obj.cars.add(car)
        messages.success(request, f"{car.title} added to wishlist.")
        
    # Redirect back to the previous page
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def toggle_wishlist_accessory(request, accessory_id):
    accessory = get_object_or_404(Accessory, pk=accessory_id)
    wishlist_obj, created = Wishlist.objects.get_or_create(user=request.user)
    
    if accessory in wishlist_obj.accessories.all():
        wishlist_obj.accessories.remove(accessory)
        messages.info(request, f"{accessory.title} removed from wishlist.")
    else:
        wishlist_obj.accessories.add(accessory)
        messages.success(request, f"{accessory.title} added to wishlist.")
        
    # Redirect back to the previous page
    return redirect(request.META.get('HTTP_REFERER', 'grid'))

    # Redirect back to the previous page
    return redirect(request.META.get('HTTP_REFERER', 'grid'))

@login_required
def wishlist_add_all_to_cart(request):
    widthlist_obj, created = Wishlist.objects.get_or_create(user=request.user)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    accessories = widthlist_obj.accessories.all()
    count_added = 0
    
    for accessory in accessories:
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, accessory=accessory)
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()
        count_added += 1
        
    if count_added > 0:
        messages.success(request, f"Added {count_added} items from wishlist to cart.")
    else:
        messages.info(request, "No accessories in wishlist to add.")
        
    return redirect('shopping_cart')

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'checkout.html', {
        'cart': cart,
        'cart_items': cart.items.all(),
        'active_page': 'checkout'
    })

@login_required
def process_checkout(request):
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        if not cart.items.exists():
             messages.error(request, "Your cart is empty.")
             return redirect('shopping_cart')

        # Get data from form or user profile
        # For this iteration we assume we use user profile data if not provided
        # or just take what's in the form that we'll add to checkout.html
        full_name = request.POST.get('full_name') or f"{request.user.first_name} {request.user.last_name}"
        email = request.POST.get('email') or request.user.email
        
        # Safe access to profile
        phone = request.POST.get('phone')
        if not phone and hasattr(request.user, 'profile'):
            phone = request.user.profile.phone
            
        address = request.POST.get('address')
        if not address and hasattr(request.user, 'profile'):
            address = request.user.profile.address
            
        city = request.POST.get('city')
        if not city and hasattr(request.user, 'profile'):
            city = request.user.profile.city
            
        # Fallbacks
        phone = phone or ""
        address = address or "Not provided" 
        city = city or "Not provided"
        
        # Calculate total
        total_price = cart.total_price()
        
        # Create Order
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            total_price=total_price,
            status='Pending'
        )
        
        # Create Order Items and notify sellers
        sellers_accessories = {}
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                accessory=item.accessory,
                quantity=item.quantity,
                price=item.accessory.price
            )
            if item.accessory.seller:
                if item.accessory.seller not in sellers_accessories:
                    sellers_accessories[item.accessory.seller] = []
                sellers_accessories[item.accessory.seller].append(item.accessory.title)
        
        # Notify sellers
        for seller, titles in sellers_accessories.items():
            accessory_titles_joined = ", ".join(titles)
            Notification.objects.create(
                user=seller,
                message=f"You have received a new order for accessories {accessory_titles_joined}!"
            )
        
        # Clear the cart
        cart.items.all().delete()
        
        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect(f'/car/order/success/?order_id={order.id}')
        
    return redirect('checkout')

@login_required
def checkout_method(request):
    return render(request, 'checkout-method.html', {'active_page': 'checkout'})

@login_required
def checkout_billing_info(request):
    return render(request, 'checkout-billing-info.html', {'active_page': 'checkout'})

def multiple_addresses(request):
    return render(request, 'multiple-addresses.html')

@login_required
def car_checkout(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        
        order = CarOrder.objects.create(
            user=request.user,
            car=car,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            total_price=car.price or 0,
            status='Pending'
        )
        # Notify the seller
        if car.seller:
            Notification.objects.create(
                user=car.seller,
                message=f"You have received a new purchase order for your car: {car.title}"
            )
            
        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_success')
        
    return render(request, 'car_checkout.html', {'car': car})

def order_success(request):
    order_id = request.GET.get('order_id')
    order = None
    if order_id:
        try:
            # Try to get accessory order first
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
             # Fallback to car order if we unify the view, or simply pass null
             pass
             
    return render(request, 'order_success.html', {'order': order})

def newsletter(request):
    if request.method == 'POST':
        messages.success(request, 'Thank you for subscribing to our newsletter!')
        return redirect('index')
    return render(request, 'newsletter.html')

def quickview(request):
    return render(request, 'quickview.html')

def compare(request):
    return render(request, 'compare.html')

# Notifications Views
@login_required
def notifications_view(request):
    """Display all notifications for the logged-in user with filtering options"""
    filter_status = request.GET.get('status', 'all')  # all, unread, read
    
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Apply filter
    if filter_status == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_status == 'read':
        notifications = notifications.filter(is_read=True)
    
    # Get counts for filter tabs
    total_count = Notification.objects.filter(user=request.user).count()
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    read_count = Notification.objects.filter(user=request.user, is_read=True).count()
    
    context = {
        'notifications': notifications,
        'filter_status': filter_status,
        'total_count': total_count,
        'unread_count': unread_count,
        'read_count': read_count,
    }
    return render(request, 'notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    messages.success(request, 'Notification marked as read.')
    return redirect('notifications')

@login_required
def mark_all_notifications_read(request):
    """Mark all unread notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications')

@login_required
def delete_notification(request, notification_id):
    """Delete a specific notification"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    messages.success(request, 'Notification deleted successfully.')
    return redirect('notifications')
