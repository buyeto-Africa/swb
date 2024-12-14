# apps/staff/serializers.py

from rest_framework import serializers
from .models import StaffRole, StaffProfile, StaffInvitation
from apps.userauths.models import User

class StaffRoleSerializer(serializers.ModelSerializer):
    staff_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = StaffRole
        fields = ['id', 'name', 'permissions', 'description', 'staff_count', 'is_active']
        read_only_fields = ['staff_count']

    def validate_permissions(self, value):
        required_keys = ['allowed_actions']
        if not all(key in value for key in required_keys):
            raise serializers.ValidationError("Permissions must contain 'allowed_actions'")
        if not isinstance(value['allowed_actions'], list):
            raise serializers.ValidationError("allowed_actions must be a list")
        return value

class StaffProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    permissions = serializers.JSONField(source='role.permissions', read_only=True)
    last_login = serializers.DateTimeField(read_only=True)

    class Meta:
        model = StaffProfile
        fields = [
            'id', 'email', 'role', 'role_name', 
            'permissions', 'is_active', 'last_login',
            'assigned_at', 'notes'
        ]
        read_only_fields = ['assigned_at']

class StaffInvitationSerializer(serializers.ModelSerializer):
    invited_by_email = serializers.EmailField(source='invited_by.email', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = StaffInvitation
        fields = [
            'id', 'email', 'role', 'role_name', 
            'token', 'is_accepted', 'created_at', 
            'expires_at', 'invited_by_email', 'attempts'
        ]
        read_only_fields = ['token', 'created_at', 'expires_at', 'attempts']

class StaffRegistrationSerializer(serializers.ModelSerializer):
    invitation_token = serializers.UUIDField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'phone', 'password', 'invitation_token']

    def validate(self, data):
        try:
            invitation = StaffInvitation.objects.get(
                token=data['invitation_token'],
                email=data['email']
            )
            if invitation.is_expired:
                invitation.increment_attempts()
                raise serializers.ValidationError({
                    "invitation": "Invitation link has expired"
                })
            if invitation.is_accepted:
                raise serializers.ValidationError({
                    "invitation": "This invitation has already been used"
                })
            return data
        except StaffInvitation.DoesNotExist:
            raise serializers.ValidationError({
                "invitation": "Invalid invitation token"
            })

    def create(self, validated_data):
        invitation_token = validated_data.pop('invitation_token')
        validated_data['user_type'] = 'staff'
        validated_data['is_email_verified'] = True
        validated_data['is_staff'] = True
        
        # Create the user
        user = User.objects.create_user(**validated_data)
        
        # Mark invitation as used
        invitation = StaffInvitation.objects.get(token=invitation_token)
        invitation.mark_as_used()
        
        return user