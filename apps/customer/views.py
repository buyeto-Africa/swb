from django.shortcuts import render

# Create your views here.


# apps/customers/views.py
from apps.userauths.models import User
import uuid 
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomerProfile
from .serializers import CustomerProfileSerializer, CustomerEmailVerificationSerializer

class CustomerProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomerProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        serializer = CustomerEmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email_verification_token=serializer.validated_data['token'])
            user.is_email_verified = True
            user.email_verification_token = None
            user.save()
            return Response({"message": "Email verified successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def resend_verification(self, request):
        user = request.user
        if user.is_email_verified:
            return Response(
                {"message": "Email already verified"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.email_verification_token = uuid.uuid4()
        user.email_verification_sent_at = timezone.now()
        user.save()

        # Send verification email
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={user.email_verification_token}"
        send_mail(
            'Verify your email',
            f'Click the link to verify your email: {verification_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "Verification email sent"})