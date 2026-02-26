import { fail, redirect } from '@sveltejs/kit';
import { graphqlRequest } from '$lib/server/graphql';
import { UPDATE_PROJECT_MUTATION, DELETE_PROJECT_MUTATION } from '$lib/graphql/mutations/project';
import { CREATE_BOARD_MUTATION } from '$lib/graphql/mutations/board';
import type { Actions } from './$types';

export const actions: Actions = {
	createBoard: async ({ request, fetch, locals, params }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const name = formData.get('name') as string;

		if (!name?.trim()) return fail(400, { error: '보드 이름을 입력하세요.' });

		try {
			const data = await graphqlRequest<{
				createBoard: { board: { id: string } };
			}>(
				fetch,
				CREATE_BOARD_MUTATION,
				{ input: { projectId: params.projectId, name: name.trim() } },
				accessToken
			);
			redirect(
				303,
				`/orgs/${params.orgId}/projects/${params.projectId}/boards/${data.createBoard.board.id}`
			);
		} catch (e) {
			if (e instanceof Response || (e as { status?: number }).status === 303) throw e;
			return fail(400, { error: e instanceof Error ? e.message : '보드 생성에 실패했습니다.' });
		}
	},

	update: async ({ request, fetch, locals, params }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const name = formData.get('name') as string;
		const description = formData.get('description') as string;

		if (!name?.trim()) return fail(400, { error: '이름을 입력하세요.' });

		try {
			await graphqlRequest(
				fetch,
				UPDATE_PROJECT_MUTATION,
				{
					input: {
						projectId: params.projectId,
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
				DELETE_PROJECT_MUTATION,
				{ id: params.projectId },
				accessToken
			);
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '삭제에 실패했습니다.' });
		}

		redirect(303, `/orgs/${params.orgId}`);
	}
};
