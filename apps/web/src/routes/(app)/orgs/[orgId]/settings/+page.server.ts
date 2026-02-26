import { fail, redirect } from '@sveltejs/kit';
import { graphqlRequest } from '$lib/server/graphql';
import {
	UPDATE_ORGANIZATION_MUTATION,
	DELETE_ORGANIZATION_MUTATION
} from '$lib/graphql/mutations/organization';
import type { Actions } from './$types';

export const actions: Actions = {
	update: async ({ request, fetch, locals, params }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const name = formData.get('name') as string;
		const description = formData.get('description') as string;

		if (!name?.trim()) return fail(400, { error: '이름을 입력하세요.' });

		try {
			await graphqlRequest(
				fetch,
				UPDATE_ORGANIZATION_MUTATION,
				{
					input: {
						organizationId: params.orgId,
						name: name.trim(),
						description: description?.trim() || ''
					}
				},
				accessToken
			);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '수정에 실패했습니다.' });
		}
	},

	delete: async ({ fetch, locals, params }) => {
		const accessToken = locals.accessToken;

		try {
			await graphqlRequest(
				fetch,
				DELETE_ORGANIZATION_MUTATION,
				{ id: params.orgId },
				accessToken
			);
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '삭제에 실패했습니다.' });
		}

		redirect(303, '/orgs');
	}
};
