import graphene
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from graphql import GraphQLError

from organizations.decorators import (
    org_role_required,
)
from organizations.models import (
    Organization,
    OrganizationMembership,
    Role,
)
from organizations.types import (
    CreateOrganizationInput,
    InviteMemberInput,
    OrganizationMemberType,
    OrganizationType,
    RemoveMemberInput,
    TransferOwnershipInput,
    UpdateMemberRoleInput,
    UpdateOrganizationInput,
)
from users.decorators import login_required
from users.models import CustomUser

# ── Organization CRUD ──


class CreateOrganization(graphene.Mutation):
    class Arguments:
        input = CreateOrganizationInput(required=True)

    organization = graphene.Field(OrganizationType)

    @login_required
    def mutate(root, info, input):
        user = info.context.user
        data = {k: v for k, v in dict(input).items() if v is not None}

        org = Organization(created_by=user, **data)

        exclude = [f.name for f in org._meta.fields if f.name not in data]
        try:
            org.clean_fields(exclude=exclude)
        except DjangoValidationError as e:
            messages = []
            for field, errors in e.message_dict.items():
                messages.extend(errors)
            raise GraphQLError("; ".join(messages))

        org.save()
        OrganizationMembership.objects.create(
            organization=org, user=user, role=Role.OWNER
        )
        return CreateOrganization(organization=org)


class UpdateOrganization(graphene.Mutation):
    class Arguments:
        input = UpdateOrganizationInput(required=True)

    organization = graphene.Field(OrganizationType)

    @org_role_required(min_role=Role.ADMIN)
    def mutate(root, info, input):
        try:
            org = Organization.objects.get(pk=input.organization_id)
        except Organization.DoesNotExist:
            raise GraphQLError("Organization을 찾을 수 없습니다.")

        data = {
            k: v
            for k, v in dict(input).items()
            if v is not None and k != "organization_id"
        }
        if not data:
            return UpdateOrganization(organization=org)

        if "name" in data:
            org.slug = ""

        for field, value in data.items():
            setattr(org, field, value)

        exclude = [f.name for f in org._meta.fields if f.name not in data]
        try:
            org.clean_fields(exclude=exclude)
        except DjangoValidationError as e:
            messages = []
            for field, errors in e.message_dict.items():
                messages.extend(errors)
            raise GraphQLError("; ".join(messages))

        org.save()
        return UpdateOrganization(organization=org)


class DeleteOrganization(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @org_role_required(min_role=Role.OWNER)
    def mutate(root, info, id):
        try:
            org = Organization.objects.get(pk=id)
        except Organization.DoesNotExist:
            raise GraphQLError("Organization을 찾을 수 없습니다.")

        org.delete()
        return DeleteOrganization(success=True)


# ── Member Management ──


class InviteMember(graphene.Mutation):
    class Arguments:
        input = InviteMemberInput(required=True)

    membership = graphene.Field(OrganizationMemberType)

    @org_role_required(min_role=Role.ADMIN)
    def mutate(root, info, input):
        try:
            Organization.objects.get(pk=input.organization_id)
        except Organization.DoesNotExist:
            raise GraphQLError("Organization을 찾을 수 없습니다.")

        try:
            target_user = CustomUser.objects.get(email=input.email)
        except CustomUser.DoesNotExist:
            raise GraphQLError("해당 이메일의 사용자를 찾을 수 없습니다.")

        if OrganizationMembership.objects.filter(
            organization_id=input.organization_id, user=target_user
        ).exists():
            raise GraphQLError("이미 이 Organization의 멤버입니다.")

        membership = OrganizationMembership.objects.create(
            organization_id=input.organization_id,
            user=target_user,
            role=Role.MEMBER,
            invited_by=info.context.user,
        )
        return InviteMember(membership=membership)


class UpdateMemberRole(graphene.Mutation):
    class Arguments:
        input = UpdateMemberRoleInput(required=True)

    membership = graphene.Field(OrganizationMemberType)

    @org_role_required(min_role=Role.ADMIN)
    def mutate(root, info, input):
        new_role = input.role
        if new_role not in [Role.ADMIN, Role.MEMBER]:
            raise GraphQLError(
                "역할은 'admin' 또는 'member'만 지정할 수 있습니다. "
                "Owner 이전은 transferOwnership을 사용하세요."
            )

        try:
            target_membership = OrganizationMembership.objects.get(
                organization_id=input.organization_id, user_id=input.user_id
            )
        except OrganizationMembership.DoesNotExist:
            raise GraphQLError("해당 멤버를 찾을 수 없습니다.")

        actor_membership = info.context.membership
        if target_membership.role == Role.OWNER:
            raise GraphQLError("Owner의 역할은 변경할 수 없습니다.")

        if (
            actor_membership.role == Role.ADMIN
            and target_membership.role == Role.ADMIN
            and new_role != Role.ADMIN
        ):
            raise GraphQLError("Admin은 다른 Admin의 역할을 변경할 수 없습니다.")

        target_membership.role = new_role
        target_membership.save(update_fields=["role"])
        return UpdateMemberRole(membership=target_membership)


class RemoveMember(graphene.Mutation):
    class Arguments:
        input = RemoveMemberInput(required=True)

    success = graphene.Boolean()

    @org_role_required(min_role=Role.ADMIN)
    def mutate(root, info, input):
        try:
            target_membership = OrganizationMembership.objects.get(
                organization_id=input.organization_id, user_id=input.user_id
            )
        except OrganizationMembership.DoesNotExist:
            raise GraphQLError("해당 멤버를 찾을 수 없습니다.")

        if target_membership.role == Role.OWNER:
            raise GraphQLError("Owner는 제거할 수 없습니다.")

        actor_membership = info.context.membership
        if (
            actor_membership.role == Role.ADMIN
            and target_membership.role != Role.MEMBER
        ):
            raise GraphQLError("Admin은 Member만 제거할 수 있습니다.")

        target_membership.delete()
        return RemoveMember(success=True)


class TransferOwnership(graphene.Mutation):
    class Arguments:
        input = TransferOwnershipInput(required=True)

    organization = graphene.Field(OrganizationType)

    @org_role_required(min_role=Role.OWNER)
    def mutate(root, info, input):
        try:
            target_membership = OrganizationMembership.objects.get(
                organization_id=input.organization_id, user_id=input.user_id
            )
        except OrganizationMembership.DoesNotExist:
            raise GraphQLError("해당 멤버를 찾을 수 없습니다.")

        actor_membership = info.context.membership
        if actor_membership.pk == target_membership.pk:
            raise GraphQLError("자기 자신에게 Ownership을 이전할 수 없습니다.")

        with transaction.atomic():
            target_membership.role = Role.OWNER
            target_membership.save(update_fields=["role"])
            actor_membership.role = Role.ADMIN
            actor_membership.save(update_fields=["role"])

        org = Organization.objects.get(pk=input.organization_id)
        return TransferOwnership(organization=org)


class OrganizationMutation(graphene.ObjectType):
    create_organization = CreateOrganization.Field()
    update_organization = UpdateOrganization.Field()
    delete_organization = DeleteOrganization.Field()
    invite_member = InviteMember.Field()
    update_member_role = UpdateMemberRole.Field()
    remove_member = RemoveMember.Field()
    transfer_ownership = TransferOwnership.Field()
