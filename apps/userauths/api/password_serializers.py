# apps/userauths/api/password_serializers.py

from rest_framework import serializers
from apps.userauths.models import User, PasswordReset
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

        




class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'error':'No account found with this email'
                })

# apps/userauths/api/password_serializers.py



# apps/userauths/api/password_serializers.py



# apps/userauths/api/password_serializers.py

from rest_framework import serializers
from django.utils import timezone
from apps.userauths.models import User, PasswordReset

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            # Return the exact error message expected by the tests
            raise serializers.ValidationError("Passwords don't match")

        try:
            reset_request = PasswordReset.objects.get(token=data['token'])
            if reset_request.is_expired():
                raise serializers.ValidationError('Reset token has expired')
            
            data['reset_request'] = reset_request
            data['user'] = reset_request.user
            return data
            
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError('Invalid reset token')

    def create(self, validated_data):
        user = validated_data['user']
        reset_request = validated_data['reset_request']
        
        user.set_password(validated_data['new_password'])
        user.save()
        
        reset_request.used_at = timezone.now()
        reset_request.save()
        
        return validated_data


# apps/userauths/api/password_serializers.py

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'error': "New passwords don't match"
            })
        
        user = self.context['request'].user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({
                'error': "Current password is incorrect"
            })

        try:
            validate_password(data['new_password'], user=user)
        except ValidationError as e:
            raise serializers.ValidationError({
                'error': str(e)
            })

        return data