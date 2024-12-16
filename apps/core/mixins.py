# apps/core/mixins.py

from django.db import models
from decimal import Decimal
from .services.currency import CurrencyConverter

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# apps/core/mixins.py

class PriceConversionMixin:
    def convert_price_fields(self, obj, request):
        """Convert price fields based on location or user preference"""
        try:
            # Get target currency from request
            target_currency = CurrencyService.get_currency_for_request(request)
            base_currency = settings.BASE_CURRENCY

            # Convert all price fields
            for field in self.price_fields:
                original_price = getattr(obj, field)
                if original_price:
                    converted_price = CurrencyConverter.convert_price(
                        Decimal(str(original_price)),
                        base_currency,
                        target_currency
                    )
                    setattr(obj, f"{field}_converted", converted_price)
                    setattr(obj, "currency", target_currency)
        except Exception as e:
            print(f"Error converting prices: {e}")

        return obj