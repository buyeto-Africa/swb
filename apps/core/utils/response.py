# apps/core/utils/response.py

def add_currency_info(data, request):
    """Add currency information to API response"""
    currency = CurrencyService.get_currency_for_request(request)
    currency_info = settings.SUPPORTED_CURRENCIES.get(currency, {})
    
    return {
        'data': data,
        'currency': {
            'code': currency,
            'name': currency_info.get('name'),
            'symbol': currency_info.get('symbol')
        }
    }