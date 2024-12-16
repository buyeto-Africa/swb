from django.test import TestCase

# Create your tests here.
# apps/store/tests.py
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from decimal import Decimal
from apps.userauths.models import User
from apps.product.models import Product
from .models import Cart, CartItem
from apps.vendor.models import VendorProfile

class CartTests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            phone='+1234567890'
        )
        
        # Create vendor user
        self.vendor = User.objects.create_user(
            email='vendor@example.com',
            password='vendorpass123',
            phone='+1234567891'
        )
        
        # Create vendor profile
        self.vendor_profile = VendorProfile.objects.create(user=self.vendor)
        
        # Create test products with vendor profile and unique SKUs
        self.product1 = Product.objects.create(
            name='Test Product 1',
            price=Decimal('10.00'),
            stock_quantity=10,
            vendor=self.vendor_profile,
            sku='TEST-SKU-001'  # Add unique SKU
        )
        
        self.product2 = Product.objects.create(
            name='Test Product 2',
            price=Decimal('20.00'),
            stock_quantity=5,
            vendor=self.vendor_profile,
            sku='TEST-SKU-002'  # Add unique SKU
        )
        
        # Authenticate the test client
        self.client.force_authenticate(user=self.user)
        
        # Create cart
        self.cart = Cart.objects.create(user=self.user)

    def test_add_item_to_cart(self):
        """Test adding an item to the cart"""
        url = reverse('cart-add-item')
        data = {
            'product_id': self.product1.id,
            'quantity': 2
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.cart.items.count(), 1)
        self.assertEqual(self.cart.items.first().quantity, 2)

    def test_add_existing_item_to_cart(self):
        """Test adding more quantity to existing cart item"""
        # First add
        CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=1
        )
        
        url = reverse('cart-add-item')
        data = {
            'product_id': self.product1.id,
            'quantity': 2
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.cart.items.count(), 1)
        self.assertEqual(self.cart.items.first().quantity, 3)

    def test_remove_item_from_cart(self):
        """Test removing an item from the cart"""
        # Add item first
        CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        
        url = reverse('cart-remove-item')
        data = {'product_id': self.product1.id}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.cart.items.count(), 0)

    def test_update_item_quantity(self):
        """Test updating item quantity in cart"""
        # Add item first
        CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        
        url = reverse('cart-update-quantity')
        data = {
            'product_id': self.product1.id,
            'quantity': 5
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.cart.items.first().quantity, 5)

    def test_cart_total_calculation(self):
        """Test cart total amount calculation"""
        CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        CartItem.objects.create(
            cart=self.cart,
            product=self.product2,
            quantity=1
        )
        
        expected_total = (
            Decimal('10.00') * 2 +  # product1
            Decimal('20.00') * 1    # product2
        )
        
        self.assertEqual(self.cart.total_amount, expected_total)

    def test_add_invalid_product(self):
        """Test adding non-existent product to cart"""
        url = reverse('cart-add-item')
        data = {
            'product_id': 999,  # Non-existent product
            'quantity': 1
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_invalid_quantity(self):
        """Test adding invalid quantity to cart"""
        url = reverse('cart-add-item')
        data = {
            'product_id': self.product1.id,
            'quantity': -1  # Invalid quantity
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)