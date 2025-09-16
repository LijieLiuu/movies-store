from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item, CheckoutFeedback
from django.views.decorators.http import require_POST

def add(request, id):
    get_object_or_404(Movie, id=id)

    qty_raw = request.POST.get('quantity', '1')
    try:
        qty = max(1, min(10, int(qty_raw)))
    except ValueError:
        qty = 1

    cart = request.session.get('cart', {})
    cart[str(id)] = str(qty)
    request.session['cart'] = cart
    return redirect('cart.index')


def index(request):
    cart = request.session.get('cart', {})
    movie_ids = [int(k) for k in cart.keys()]

    movies_in_cart = []
    cart_total = 0
    if movie_ids:
        movies_in_cart = Movie.objects.filter(id__in=movie_ids).order_by('id')
        cart_total = calculate_cart_total(cart, movies_in_cart)

    template_data = {
        'title': 'Cart',
        'movies_in_cart': movies_in_cart,
        'cart_total': cart_total,
    }
    return render(request, 'cart/index.html', {'template_data': template_data})


def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')


@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())

    if not movie_ids:
        return redirect('cart.index')

    movies_in_cart = Movie.objects.filter(id__in=movie_ids).order_by('id')
    cart_total = calculate_cart_total(cart, movies_in_cart)

    order = Order.objects.create(user=request.user, total=cart_total)

    for movie in movies_in_cart:
        Item.objects.create(
            movie=movie,
            price=movie.price,
            order=order,
            quantity=int(cart[str(movie.id)]),
        )

    request.session['cart'] = {}

    template_data = {
        'title': 'Purchase confirmation',
        'order_id': order.id,
    }
    return render(request, 'cart/purchase.html', {'template_data': template_data})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def feedback_index(request):
    template_data = {
        'title': 'Checkout Feedback',
        'feedbacks': CheckoutFeedback.objects.all().order_by('-date'),
    }
    return render(request, 'cart/feedback_index.html', {'template_data': template_data})

@require_POST
@login_required
def feedback_create(request):
    name = (request.POST.get('name') or '').strip()
    comment = (request.POST.get('comment') or '').strip()
    order_id = request.POST.get('order_id')

    if comment:
        order = None
        if order_id:
            try:
                order = Order.objects.get(id=order_id, user=request.user)
            except Order.DoesNotExist:
                order = None
        CheckoutFeedback.objects.create(name=name, comment=comment, order=order)
    return redirect('home.index')