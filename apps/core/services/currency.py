# apps/core/services/currency.py

import requests
from django.core.cache import cache
from decimal import Decimal
from ..exceptions import CurrencyConversionError

class CurrencyConverter:
    CACHE_KEY_PREFIX = "exchange_rate_"
    CACHE_TIMEOUT = 3600  # 1 hour

    @classmethod
    def get_exchange_rate(cls, from_currency: str, to_currency: str) -> Decimal:
        cache_key = f"{cls.CACHE_KEY_PREFIX}{from_currency}_{to_currency}"
        
        # Try to get rate from cache first
        rate = cache.get(cache_key)
        if rate:
            return Decimal(str(rate))

        try:
            response = requests.get(
                f"https://api.exchangerate-api.com/v4/latest/{from_currency}",
                timeout=5
            )
            data = response.json()
            rate = Decimal(str(data['rates'][to_currency]))
            
            # Cache the rate
            cache.set(cache_key, str(rate), cls.CACHE_TIMEOUT)
            return rate
        except Exception as e:
            raise CurrencyConversionError(str(e))
        



# apps/core/services/currency.py

class CurrencyService:
    @staticmethod
    def get_currency_for_location(country_code):
        """Get default currency for a country"""
        COUNTRY_CURRENCY_MAP = {
            'US': 'USD',
            'GB': 'GBP',
            'EU': 'EUR',
            'NG': 'NGN',
            'GH': 'GHS',
            # Add more country-currency mappings
        }
        return COUNTRY_CURRENCY_MAP.get(country_code, 'USD')

    @staticmethod
    def get_currency_for_request(request):
        """Get appropriate currency for the request"""
        if hasattr(request, 'currency'):
            return request.currency
        return 'USD'