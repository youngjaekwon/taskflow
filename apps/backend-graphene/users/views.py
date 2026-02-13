from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import (
    DetailResponseSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    LogoutSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileImageSerializer,
    ProfileImageUploadResponseSerializer,
    RegisterSerializer,
    ResendVerificationEmailSerializer,
    TokenResponseSerializer,
    VerifyEmailSerializer,
)
from users.utils import (
    invalidate_all_tokens,
    send_password_reset_email,
    send_verification_email,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth"],
        request=RegisterSerializer,
        responses={201: DetailResponseSerializer},
        auth=[],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_verification_email(user)
        return Response(
            {"detail": "회원가입이 완료되었습니다. 이메일을 확인해주세요."},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth"],
        request=VerifyEmailSerializer,
        responses={200: DetailResponseSerializer},
        auth=[],
    )
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.email_verified = True
        user.save(update_fields=["email_verified"])
        return Response({"detail": "이메일 인증이 완료되었습니다."})


class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth"],
        request=ResendVerificationEmailSerializer,
        responses={200: DetailResponseSerializer},
        auth=[],
    )
    def post(self, request):
        serializer = ResendVerificationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            if not user.email_verified:
                send_verification_email(user)
        except User.DoesNotExist:
            pass  # 보안: 미등록 이메일에도 성공 응답
        return Response({"detail": "인증 메일이 발송되었습니다."})


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth"],
        request=LoginSerializer,
        responses={200: LoginResponseSerializer},
        auth=[],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        response_serializer = LoginResponseSerializer(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": user,
            }
        )
        return Response(response_serializer.data)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth"],
        request=LogoutSerializer,
        responses={
            200: DetailResponseSerializer,
            400: DetailResponseSerializer,
        },
        auth=[],
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh"]
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "유효하지 않은 토큰입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "로그아웃되었습니다."})


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["auth"],
        request=PasswordChangeSerializer,
        responses={200: TokenResponseSerializer},
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        invalidate_all_tokens(user)
        refresh = RefreshToken.for_user(user)
        response_serializer = TokenResponseSerializer(
            {
                "detail": "비밀번호가 변경되었습니다.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )
        return Response(response_serializer.data)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth"],
        request=PasswordResetRequestSerializer,
        responses={200: DetailResponseSerializer},
        auth=[],
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            send_password_reset_email(user)
        except User.DoesNotExist:
            pass  # 보안: 미등록 이메일에도 성공 응답
        return Response({"detail": "비밀번호 초기화 메일이 발송되었습니다."})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth"],
        request=PasswordResetConfirmSerializer,
        responses={200: DetailResponseSerializer},
        auth=[],
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        invalidate_all_tokens(user)
        return Response({"detail": "비밀번호가 초기화되었습니다."})


class UserProfileImageView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @extend_schema(
        tags=["users"],
        request={"multipart/form-data": ProfileImageSerializer},
        responses={200: ProfileImageUploadResponseSerializer},
    )
    def put(self, request):
        serializer = ProfileImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if user.profile_image:
            user.profile_image.delete(save=False)
        user.profile_image = serializer.validated_data["image"]
        user.save(update_fields=["profile_image"])
        response_serializer = ProfileImageUploadResponseSerializer(
            {
                "detail": "프로필 이미지가 업로드되었습니다.",
                "profile_image_url": request.build_absolute_uri(user.profile_image.url),
            }
        )
        return Response(response_serializer.data)

    @extend_schema(
        tags=["users"],
        request=None,
        responses={204: None},
    )
    def delete(self, request):
        user = request.user
        if user.profile_image:
            user.profile_image.delete(save=False)
            user.profile_image = None
            user.save(update_fields=["profile_image"])
        return Response(status=status.HTTP_204_NO_CONTENT)
