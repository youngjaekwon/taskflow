import json

import pytest
from django.urls import reverse

from conftest import make_auth_client
from organizations.models import OrganizationMembership, Role

GRAPHQL_URL = reverse("graphql")

INVITE_MEMBER = """
    mutation InviteMember($input: InviteMemberInput!) {
        inviteMember(input: $input) {
            membership {
                user {
                    id
                    email
                }
                role
            }
        }
    }
"""

UPDATE_MEMBER_ROLE = """
    mutation UpdateMemberRole($input: UpdateMemberRoleInput!) {
        updateMemberRole(input: $input) {
            membership {
                user {
                    id
                }
                role
            }
        }
    }
"""

REMOVE_MEMBER = """
    mutation RemoveMember($input: RemoveMemberInput!) {
        removeMember(input: $input) {
            success
        }
    }
"""

TRANSFER_OWNERSHIP = """
    mutation TransferOwnership($input: TransferOwnershipInput!) {
        transferOwnership(input: $input) {
            organization {
                id
                name
            }
        }
    }
"""


@pytest.mark.django_db
class TestInviteMember:
    def test_owner_can_invite(self, auth_client, org_with_owner, user_factory):
        user_factory(email="invitee@example.com", email_verified=True)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": INVITE_MEMBER,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "email": "invitee@example.com",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        membership = data["data"]["inviteMember"]["membership"]
        assert membership["user"]["email"] == "invitee@example.com"
        assert membership["role"] == "MEMBER"

    def test_admin_can_invite(self, org_with_owner, admin_user, user_factory):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=admin_user, role=Role.ADMIN
        )
        user_factory(email="admin_invite@example.com", email_verified=True)
        client = make_auth_client(admin_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": INVITE_MEMBER,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "email": "admin_invite@example.com",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["inviteMember"]["membership"]["role"] == "MEMBER"

    def test_member_cannot_invite(self, org_with_owner, member_user, user_factory):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=member_user, role=Role.MEMBER
        )
        user_factory(email="target@example.com")
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": INVITE_MEMBER,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "email": "target@example.com",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "권한이 부족합니다."

    def test_invite_nonexistent_email(self, auth_client, org_with_owner):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": INVITE_MEMBER,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "email": "noone@example.com",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        expected = "해당 이메일의 사용자를 찾을 수 없습니다."
        assert data["errors"][0]["message"] == expected

    def test_invite_already_member(self, auth_client, org_with_owner, user_factory):
        target = user_factory(email="already@example.com")
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=target, role=Role.MEMBER
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": INVITE_MEMBER,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "email": "already@example.com",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "이미 이 Organization의 멤버입니다."


@pytest.mark.django_db
class TestUpdateMemberRole:
    def test_owner_can_change_member_to_admin(
        self, auth_client, org_with_owner, member_user
    ):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=member_user, role=Role.MEMBER
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_MEMBER_ROLE,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "userId": str(member_user.id),
                            "role": "admin",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updateMemberRole"]["membership"]["role"] == "ADMIN"

    def test_owner_can_change_admin_to_member(
        self, auth_client, org_with_owner, admin_user
    ):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=admin_user, role=Role.ADMIN
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_MEMBER_ROLE,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "userId": str(admin_user.id),
                            "role": "member",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updateMemberRole"]["membership"]["role"] == "MEMBER"

    def test_cannot_set_role_to_owner(self, auth_client, org_with_owner, member_user):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=member_user, role=Role.MEMBER
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_MEMBER_ROLE,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "userId": str(member_user.id),
                            "role": "owner",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert "transferOwnership" in data["errors"][0]["message"]

    def test_admin_cannot_change_other_admin(
        self, org_with_owner, admin_user, user_factory
    ):
        other_admin = user_factory(email_verified=True)
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=admin_user, role=Role.ADMIN
        )
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=other_admin, role=Role.ADMIN
        )
        client = make_auth_client(admin_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_MEMBER_ROLE,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "userId": str(other_admin.id),
                            "role": "member",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert "Admin" in data["errors"][0]["message"]

    def test_cannot_change_owner_role(self, org_with_owner, admin_user, verified_user):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=admin_user, role=Role.ADMIN
        )
        client = make_auth_client(admin_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_MEMBER_ROLE,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "userId": str(verified_user.id),
                            "role": "admin",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert "Owner" in data["errors"][0]["message"]


@pytest.mark.django_db
class TestRemoveMember:
    def test_owner_can_remove_member(self, auth_client, org_with_owner, member_user):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=member_user, role=Role.MEMBER
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": REMOVE_MEMBER,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "userId": str(member_user.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["removeMember"]["success"] is True
        assert not OrganizationMembership.objects.filter(
            organization=org_with_owner, user=member_user
        ).exists()

    def test_owner_can_remove_admin(self, auth_client, org_with_owner, admin_user):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=admin_user, role=Role.ADMIN
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": REMOVE_MEMBER,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "userId": str(admin_user.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["removeMember"]["success"] is True

    def test_admin_can_remove_member(self, org_with_owner, admin_user, member_user):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=admin_user, role=Role.ADMIN
        )
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=member_user, role=Role.MEMBER
        )
        client = make_auth_client(admin_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": REMOVE_MEMBER,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "userId": str(member_user.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["removeMember"]["success"] is True

    def test_admin_cannot_remove_other_admin(
        self, org_with_owner, admin_user, user_factory
    ):
        other_admin = user_factory(email_verified=True)
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=admin_user, role=Role.ADMIN
        )
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=other_admin, role=Role.ADMIN
        )
        client = make_auth_client(admin_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": REMOVE_MEMBER,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "userId": str(other_admin.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert "Member만" in data["errors"][0]["message"]

    def test_cannot_remove_owner(self, org_with_owner, admin_user, verified_user):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=admin_user, role=Role.ADMIN
        )
        client = make_auth_client(admin_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": REMOVE_MEMBER,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "userId": str(verified_user.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert "Owner" in data["errors"][0]["message"]

    def test_member_cannot_remove(self, org_with_owner, member_user, user_factory):
        other = user_factory()
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=member_user, role=Role.MEMBER
        )
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=other, role=Role.MEMBER
        )
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": REMOVE_MEMBER,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "userId": str(other.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "권한이 부족합니다."


@pytest.mark.django_db
class TestTransferOwnership:
    def test_owner_can_transfer(
        self, auth_client, org_with_owner, admin_user, verified_user
    ):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=admin_user, role=Role.ADMIN
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": TRANSFER_OWNERSHIP,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "userId": str(admin_user.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["transferOwnership"]["organization"] is not None

        new_owner = OrganizationMembership.objects.get(
            organization=org_with_owner, user=admin_user
        )
        assert new_owner.role == Role.OWNER

        old_owner = OrganizationMembership.objects.get(
            organization=org_with_owner, user=verified_user
        )
        assert old_owner.role == Role.ADMIN

    def test_admin_cannot_transfer(self, org_with_owner, admin_user, member_user):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=admin_user, role=Role.ADMIN
        )
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=member_user, role=Role.MEMBER
        )
        client = make_auth_client(admin_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": TRANSFER_OWNERSHIP,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "userId": str(member_user.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "권한이 부족합니다."

    def test_cannot_transfer_to_self(self, auth_client, org_with_owner, verified_user):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": TRANSFER_OWNERSHIP,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "userId": str(verified_user.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert "자기 자신" in data["errors"][0]["message"]

    def test_cannot_transfer_to_non_member(
        self, auth_client, org_with_owner, user_factory
    ):
        non_member = user_factory()
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": TRANSFER_OWNERSHIP,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "userId": str(non_member.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert "멤버를 찾을 수 없습니다" in data["errors"][0]["message"]
