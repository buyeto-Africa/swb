# # apps/core/constants.py

# SUPPORTED_CURRENCIES = [
#     ('USD', 'US Dollar'),
#     ('EUR', 'Euro'),
#     ('GBP', 'British Pound'),
#     ('NGN', 'Nigerian Naira'),
#     ('GHS', 'Ghana Cedis'),
# ]

# NOTIFICATION_TYPES = [
#     ('EMAIL', 'Email'),
#     ('SMS', 'SMS'),
#     ('PUSH', 'Push Notification'),
# ]

# SUPPORTED_LANGUAGES = [
#     ('en', 'English'),
#     ('fr', 'French'),
#     ('es', 'Spanish'),
# ]




# apps/core/constants.py

# Currency configurations with symbols and decimal places
CURRENCY_CONFIGS = {
    'USD': {
        'name': 'US Dollar',
        'symbol': '$',
        'decimal_places': 2,
        'symbol_position': 'before',  # or 'after'
        'thousands_separator': ',',
        'decimal_separator': '.'
    },
    'EUR': {
        'name': 'Euro',
        'symbol': '€',
        'decimal_places': 2,
        'symbol_position': 'before',
        'thousands_separator': '.',
        'decimal_separator': ','
    },
    'GBP': {
        'name': 'British Pound',
        'symbol': '£',
        'decimal_places': 2,
        'symbol_position': 'before',
        'thousands_separator': ',',
        'decimal_separator': '.'
    },
    'NGN': {
        'name': 'Nigerian Naira',
        'symbol': '₦',
        'decimal_places': 2,
        'symbol_position': 'before',
        'thousands_separator': ',',
        'decimal_separator': '.'
    },
    'GHS': {
        'name': 'Ghana Cedis',
        'symbol': '₵',
        'decimal_places': 2,
        'symbol_position': 'before',
        'thousands_separator': ',',
        'decimal_separator': '.'
    },
    'KES': {
        'name': 'Kenyan Shilling',
        'symbol': 'KSh',
        'decimal_places': 2,
        'symbol_position': 'before',
        'thousands_separator': ',',
        'decimal_separator': '.'
    },
    'ZAR': {
        'name': 'South African Rand',
        'symbol': 'R',
        'decimal_places': 2,
        'symbol_position': 'before',
        'thousands_separator': ',',
        'decimal_separator': '.'
    }
}

# Generate SUPPORTED_CURRENCIES list from CURRENCY_CONFIGS
SUPPORTED_CURRENCIES = [(code, config['name']) for code, config in CURRENCY_CONFIGS.items()]

# Default currency for the platform
DEFAULT_CURRENCY = 'USD'

# Notification types with additional metadata
NOTIFICATION_CONFIGS = {
    'EMAIL': {
        'name': 'Email',
        'icon': 'email',
        'requires_verification': True,
        'max_daily_limit': 50
    },
    'SMS': {
        'name': 'SMS',
        'icon': 'sms',
        'requires_verification': True,
        'max_daily_limit': 10
    },
    'PUSH': {
        'name': 'Push Notification',
        'icon': 'notifications',
        'requires_verification': False,
        'max_daily_limit': 100
    },
    'WHATSAPP': {
        'name': 'WhatsApp',
        'icon': 'whatsapp',
        'requires_verification': True,
        'max_daily_limit': 20
    }
}

# Generate NOTIFICATION_TYPES list from NOTIFICATION_CONFIGS
NOTIFICATION_TYPES = [(code, config['name']) for code, config in NOTIFICATION_CONFIGS.items()]

# Language configurations with additional metadata
LANGUAGE_CONFIGS = {
    'en': {
        'name': 'English',
        'flag': '🇬🇧',
        'rtl': False,
        'date_format': 'MM/DD/YYYY'
    },
    'fr': {
        'name': 'French',
        'flag': '🇫🇷',
        'rtl': False,
        'date_format': 'DD/MM/YYYY'
    },
    'es': {
        'name': 'Spanish',
        'flag': '🇪🇸',
        'rtl': False,
        'date_format': 'DD/MM/YYYY'
    },
    'ar': {
        'name': 'Arabic',
        'flag': '🇸🇦',
        'rtl': True,
        'date_format': 'DD/MM/YYYY'
    }
}

# Generate SUPPORTED_LANGUAGES list from LANGUAGE_CONFIGS
SUPPORTED_LANGUAGES = [(code, config['name']) for code, config in LANGUAGE_CONFIGS.items()]

# Default language for the platform
DEFAULT_LANGUAGE = 'en'

# Currency formatting helper function
def format_currency(amount, currency_code='USD'):
    """
    Format amount according to currency configuration
    """
    config = CURRENCY_CONFIGS.get(currency_code, CURRENCY_CONFIGS['USD'])
    formatted = '{:,.{precision}f}'.format(
        amount, 
        precision=config['decimal_places']
    ).replace(',', config['thousands_separator']).replace('.', config['decimal_separator'])
    
    if config['symbol_position'] == 'before':
        return f"{config['symbol']}{formatted}"
    return f"{formatted}{config['symbol']}"






