from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from users.tokens import email_verification_token


def send_verification_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    verification_url = (
        f"{settings.FRONTEND_URL}{settings.FRONTEND_VERIFY_EMAIL_PATH}?uid={uid}&token={token}"
    )
    send_mail(
        subject="이메일 인증을 완료해주세요",
        message=f"다음 링크를 클릭하여 이메일을 인증해주세요: {verification_url}",
        from_email=None,
        recipient_list=[user.email],
    )


def invalidate_all_tokens(user):
    outstanding_tokens = OutstandingToken.objects.filter(user=user)
    existing = set(
        BlacklistedToken.objects.filter(
            token__in=outstanding_tokens
        ).values_list("token_id", flat=True)
    )
    BlacklistedToken.objects.bulk_create(
        [
            BlacklistedToken(token=t)
            for t in outstanding_tokens
            if t.id not in existing
        ],
        ignore_conflicts=True,
    )


def send_password_reset_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_url = (
        f"{settings.FRONTEND_URL}{settings.FRONTEND_RESET_PASSWORD_PATH}?uid={uid}&token={token}"
    )
    send_mail(
        subject="비밀번호를 초기화해주세요",
        message=f"다음 링크를 클릭하여 비밀번호를 초기화해주세요: {reset_url}",
        from_email=None,
        recipient_list=[user.email],
    )
