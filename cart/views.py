from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item

def add(request, id):
    # 确认电影存在
    get_object_or_404(Movie, id=id)

    # 读取并校验数量（1~10）
    qty_raw = request.POST.get('quantity', '1')
    try:
        qty = max(1, min(10, int(qty_raw)))
    except ValueError:
        qty = 1

    # 简单版：直接覆盖数量（不做累加）
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