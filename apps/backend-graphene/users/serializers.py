from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from users.tokens import email_verification_token

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "비밀번호가 일치하지 않습니다."}
            )
        return data

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
        )


class VerifyEmailSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data["uid"]))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("유효하지 않은 링크입니다.")

        if not email_verification_token.check_token(user, data["token"]):
            raise serializers.ValidationError("유효하지 않거나 만료된 토큰입니다.")

        data["user"] = user
        return data


class ResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if user is None:
            raise serializers.ValidationError(
                "이메일 또는 비밀번호가 올바르지 않습니다."
            )
        if not user.email_verified:
            raise serializers.ValidationError("이메일 인증을 완료해주세요.")
        data["user"] = user
        return data


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("기존 비밀번호가 올바르지 않습니다.")
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "비밀번호가 일치하지 않습니다."}
            )
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data["uid"]))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("유효하지 않은 링크입니다.")

        if not default_token_generator.check_token(user, data["token"]):
            raise serializers.ValidationError("유효하지 않거나 만료된 토큰입니다.")

        data["user"] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name"]


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()


class TokenResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    access = serializers.CharField()
    refresh = serializers.CharField()


class ProfileImageUploadResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    profile_image_url = serializers.URLField()


class DetailResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ProfileImageSerializer(serializers.Serializer):
    image = serializers.ImageField()

    ALLOWED_TYPES = ("image/jpeg", "image/png")
    ALLOWED_FORMATS = {"JPEG", "PNG"}
    MAX_SIZE = 5 * 1024 * 1024  # 5MB

    def validate_image(self, value):
        if value.content_type not in self.ALLOWED_TYPES:
            raise serializers.ValidationError("JPEG 또는 PNG 파일만 허용됩니다.")
        if value.size > self.MAX_SIZE:
            raise serializers.ValidationError("파일 크기는 5MB를 초과할 수 없습니다.")

        from PIL import Image, UnidentifiedImageError

        try:
            img = Image.open(value)
            img.verify()
        except (UnidentifiedImageError, Exception):
            raise serializers.ValidationError("유효한 이미지 파일이 아닙니다.")

        if img.format not in self.ALLOWED_FORMATS:
            raise serializers.ValidationError("JPEG 또는 PNG 파일만 허용됩니다.")

        value.seek(0)
        return value
