# apps/core/middleware/currency.py

from django.utils.deprecation import MiddlewareMixin

class CurrencyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                request.currency = request.user.customer_profile.preferences.currency_preference
            except:
                request.currency = 'USD'
        else:
            request.currency = 'USD'