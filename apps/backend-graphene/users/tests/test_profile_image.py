import io
import tempfile

import pytest
from django.urls import reverse
from PIL import Image

PROFILE_IMAGE_URL = reverse("users:profile-image")


def create_test_image(format="JPEG", size=(100, 100)):
    image = Image.new("RGB", size, color="red")
    tmp = io.BytesIO()
    image.save(tmp, format=format)
    tmp.seek(0)
    tmp.name = f"test.{format.lower()}"
    return tmp


@pytest.mark.django_db
class TestUserProfileImageView:
    def test_upload_success(self, auth_client, verified_user, settings):
        settings.MEDIA_ROOT = tempfile.mkdtemp()
        image = create_test_image()
        response = auth_client.put(
            PROFILE_IMAGE_URL, {"image": image}, format="multipart"
        )
        assert response.status_code == 200
        verified_user.refresh_from_db()
        assert verified_user.profile_image
        assert "profile_image_url" in response.data
        assert verified_user.profile_image.name in response.data["profile_image_url"]

    def test_upload_png(self, auth_client, verified_user, settings):
        settings.MEDIA_ROOT = tempfile.mkdtemp()
        image = create_test_image(format="PNG")
        response = auth_client.put(
            PROFILE_IMAGE_URL, {"image": image}, format="multipart"
        )
        assert response.status_code == 200

    def test_upload_invalid_type(self, auth_client, settings):
        settings.MEDIA_ROOT = tempfile.mkdtemp()
        image = create_test_image(format="BMP")
        image.name = "test.bmp"
        response = auth_client.put(
            PROFILE_IMAGE_URL, {"image": image}, format="multipart"
        )
        assert response.status_code == 400

    def test_upload_too_large(self, auth_client, settings):
        settings.MEDIA_ROOT = tempfile.mkdtemp()
        # Create a large image (> 5MB)
        large_image = io.BytesIO(b"x" * (6 * 1024 * 1024))
        large_image.name = "large.jpg"
        large_image.content_type = "image/jpeg"
        response = auth_client.put(
            PROFILE_IMAGE_URL, {"image": large_image}, format="multipart"
        )
        assert response.status_code == 400

    def test_upload_unauthenticated(self, api_client, settings):
        settings.MEDIA_ROOT = tempfile.mkdtemp()
        image = create_test_image()
        response = api_client.put(
            PROFILE_IMAGE_URL, {"image": image}, format="multipart"
        )
        assert response.status_code in (401, 403)

    def test_delete_success(self, auth_client, verified_user, settings):
        settings.MEDIA_ROOT = tempfile.mkdtemp()
        # First upload
        image = create_test_image()
        auth_client.put(PROFILE_IMAGE_URL, {"image": image}, format="multipart")
        verified_user.refresh_from_db()
        assert verified_user.profile_image
        # Then delete
        response = auth_client.delete(PROFILE_IMAGE_URL)
        assert response.status_code == 204
        verified_user.refresh_from_db()
        assert not verified_user.profile_image

    def test_replace_deletes_old_file(self, auth_client, verified_user, settings):
        import os

        media_root = tempfile.mkdtemp()
        settings.MEDIA_ROOT = media_root
        # Upload first image
        image1 = create_test_image()
        auth_client.put(PROFILE_IMAGE_URL, {"image": image1}, format="multipart")
        verified_user.refresh_from_db()
        old_full_path = os.path.join(media_root, verified_user.profile_image.name)
        assert os.path.exists(old_full_path)
        # Upload second image with different name
        image2 = create_test_image(format="PNG")
        response = auth_client.put(
            PROFILE_IMAGE_URL, {"image": image2}, format="multipart"
        )
        assert response.status_code == 200
        # Old file should be deleted
        assert not os.path.exists(old_full_path)
