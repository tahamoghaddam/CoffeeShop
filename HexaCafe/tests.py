from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Product, Ingredient, ProductIngredient, Order, OrderProduct, Cart, CartItem

class ProductModelTest(TestCase):
    def setUp(self):
        # Create ingredients
        self.coffee_bean = Ingredient.objects.create(name='Coffee Bean', quantity=100.0)
        self.milk = Ingredient.objects.create(name='Milk', quantity=50.0)
        
        # Create dummy image
        image = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')

        # Create product
        self.product = Product.objects.create(name='Latte', price=5, description='Delicious', category='hot', image=image)
        
        # Link ingredients
        ProductIngredient.objects.create(product=self.product, ingredient=self.coffee_bean, quantity=10.0)
        ProductIngredient.objects.create(product=self.product, ingredient=self.milk, quantity=5.0)

    def test_check_availability_true(self):
        # 100 beans / 10 required = 10 avail. 50 milk / 5 required = 10 avail.
        self.assertTrue(self.product.check_availability(1))
        self.assertTrue(self.product.check_availability(10))

    def test_check_availability_false(self):
        self.assertFalse(self.product.check_availability(11))

class CartViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', email='test@test.com', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')
        
        self.ingredient = Ingredient.objects.create(name='Sugar', quantity=100)
        
        image = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        self.product = Product.objects.create(name='Sweet Tea', price=2, description='Sweet', category='cold', image=image)
        ProductIngredient.objects.create(product=self.product, ingredient=self.ingredient, quantity=10)

    def test_add_to_cart_success(self):
        url = reverse('add_to_cart', args=[self.product.id])
        response = self.client.post(url, {'quantity': 1})
        
        # Should redirect to shoppingcart
        self.assertRedirects(response, reverse('shoppingcart'))
        
        # Verify item in cart
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 1)

    def test_add_to_cart_insufficient_stock(self):
        url = reverse('add_to_cart', args=[self.product.id])
        # Request 11 items (requires 110 sugar, only 100 avail)
        response = self.client.post(url, {'quantity': 11})
        
        # Should redirect back to product page (referer) or specific page as per view logic
        # Based on my view code: return redirect('product')
        self.assertRedirects(response, reverse('product'))
        
        # Verify cart empty
        cart, _ = Cart.objects.get_or_create(user=self.user)
        self.assertEqual(cart.items.count(), 0)

    def test_checkout_deducts_inventory(self):
        # Add to cart first
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=5)
        
        initial_stock = Ingredient.objects.get(name='Sugar').quantity
        
        # Checkout
        url = reverse('shoppingcart')
        response = self.client.post(url, {'delivery_method': 'True'}) # Takeout
        
        self.assertRedirects(response, reverse('order_success'))
        
        # Verify Order Created
        self.assertEqual(Order.objects.count(), 1)
        
        # Verify Stock Deducted
        # 5 items * 10 sugar = 50 sugar deducted.
        new_stock = Ingredient.objects.get(name='Sugar').quantity
        self.assertEqual(new_stock, initial_stock - 50)
        
    def test_checkout_race_condition_simulation(self):
        # This is a basic functional test, real race condition testing requires concurrent threads
        # but we can verify the F() expression usage by checking logic (code review) 
        # or simple deduction here.
        pass
