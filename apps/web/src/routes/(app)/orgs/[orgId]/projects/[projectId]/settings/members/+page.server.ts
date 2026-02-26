import { fail } from '@sveltejs/kit';
import { graphqlRequest } from '$lib/server/graphql';
import {
	ADD_PROJECT_MEMBER_MUTATION,
	REMOVE_PROJECT_MEMBER_MUTATION
} from '$lib/graphql/mutations/project';
import type { Actions } from './$types';

export const actions: Actions = {
	add: async ({ request, fetch, locals, params }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const userId = formData.get('user_id') as string;

		if (!userId) return fail(400, { error: '멤버를 선택하세요.' });

		try {
			await graphqlRequest(
				fetch,
				ADD_PROJECT_MEMBER_MUTATION,
				{ input: { projectId: params.projectId, userId } },
				accessToken
			);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '멤버 추가에 실패했습니다.' });
		}
	},

	remove: async ({ request, fetch, locals, params }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const userId = formData.get('user_id') as string;

		try {
			await graphqlRequest(
				fetch,
				REMOVE_PROJECT_MEMBER_MUTATION,
				{ input: { projectId: params.projectId, userId } },
				accessToken
			);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '멤버 제거에 실패했습니다.' });
		}
	}
};
