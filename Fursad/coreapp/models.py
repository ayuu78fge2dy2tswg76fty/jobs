from django.db import models
from django.utils import timezone
import random

# Create your models here.


class PasswordResetOTP(models.Model):
    USER_TYPE_CHOICES = [
        ('company', 'Company'),
        ('shaqodon', 'Jobseeker'),
    ]
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        """OTP is valid for 10 minutes."""
        return not self.is_used and (timezone.now() - self.created_at).seconds < 600

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    def __str__(self):
        return f'{self.email} - {self.otp} ({self.user_type})'

    class Meta:
        verbose_name = 'Password Reset OTP'
        ordering = ['-created_at']
