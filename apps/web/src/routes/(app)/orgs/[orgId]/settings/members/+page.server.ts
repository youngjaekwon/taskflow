import { fail } from '@sveltejs/kit';
import { graphqlRequest } from '$lib/server/graphql';
import {
	INVITE_MEMBER_MUTATION,
	UPDATE_MEMBER_ROLE_MUTATION,
	REMOVE_MEMBER_MUTATION
} from '$lib/graphql/mutations/organization';
import type { Actions } from './$types';

export const actions: Actions = {
	invite: async ({ request, fetch, locals, params }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const email = formData.get('email') as string;

		if (!email?.trim()) return fail(400, { error: '이메일을 입력하세요.' });

		try {
			await graphqlRequest(
				fetch,
				INVITE_MEMBER_MUTATION,
				{ input: { organizationId: params.orgId, email: email.trim() } },
				accessToken
			);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '초대에 실패했습니다.' });
		}
	},

	updateRole: async ({ request, fetch, locals, params }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const userId = formData.get('user_id') as string;
		const role = formData.get('role') as string;

		try {
			await graphqlRequest(
				fetch,
				UPDATE_MEMBER_ROLE_MUTATION,
				{ input: { organizationId: params.orgId, userId, role } },
				accessToken
			);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '역할 변경에 실패했습니다.' });
		}
	},

	remove: async ({ request, fetch, locals, params }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const userId = formData.get('user_id') as string;

		try {
			await graphqlRequest(
				fetch,
				REMOVE_MEMBER_MUTATION,
				{ input: { organizationId: params.orgId, userId } },
				accessToken
			);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '멤버 제거에 실패했습니다.' });
		}
	}
};
