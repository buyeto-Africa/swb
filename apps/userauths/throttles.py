# apps/userauths/api/throttling.py

from rest_framework.throttling import SimpleRateThrottle

class PasswordResetRateThrottle(SimpleRateThrottle):
    rate = '3/min'
    scope = 'password_reset'

    def get_cache_key(self, request, view):
        email = request.data.get('email')
        if not email:
            return None
        return f"password_reset_rate_{email}"