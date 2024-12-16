# apps/core/middleware/location.py

import requests
from django.core.cache import cache
from django.conf import settings

class LocationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip for authenticated users who have set their preferences
        if request.user.is_authenticated:
            try:
                request.currency = request.user.customer_profile.preferences.currency_preference
                return self.get_response(request)
            except:
                pass

        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Try to get currency from cache first
        cache_key = f'currency_for_ip_{client_ip}'
        currency = cache.get(cache_key)

        if not currency:
            # Get location data from IP
            try:
                response = requests.get(
                    f'https://ipapi.co/{client_ip}/json/',
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    currency = data.get('currency', 'USD')
                    # Cache the result for 24 hours
                    cache.set(cache_key, currency, 60 * 60 * 24)
                else:
                    currency = 'USD'
            except:
                currency = 'USD'

        request.currency = currency
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip