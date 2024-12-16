# apps/core/exceptions.py

from rest_framework.exceptions import APIException

class CurrencyConversionError(APIException):
    status_code = 503
    default_detail = 'Currency conversion service unavailable.'
    default_code = 'currency_conversion_error'

class InvalidFileType(APIException):
    status_code = 400
    default_detail = 'Invalid file type.'
    default_code = 'invalid_file_type'