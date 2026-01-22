from .models import Cart, Notification

def car_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
        latest_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        return {
            'cart_item_count': sum(item.quantity for item in cart.items.all()),
            'cart_subtotal': cart.total_price(),
            'current_cart': cart,
            'unread_notification_count': unread_notifications_count,
            'latest_notifications': latest_notifications
        }
    return {
        'cart_item_count': 0,
        'cart_subtotal': 0,
        'current_cart': None,
        'unread_notification_count': 0,
        'latest_notifications': []
    }
