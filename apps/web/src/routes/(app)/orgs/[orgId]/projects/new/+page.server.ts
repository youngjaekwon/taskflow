import { fail, redirect, error } from '@sveltejs/kit';
import { graphqlRequest } from '$lib/server/graphql';
import { CREATE_PROJECT_MUTATION } from '$lib/graphql/mutations/project';
import type { PageServerLoad, Actions } from './$types';

export const load: PageServerLoad = async ({ parent }) => {
	const { isAdmin } = await parent();
	if (!isAdmin) error(403, '프로젝트 생성 권한이 없습니다.');
};

export const actions: Actions = {
	default: async ({ request, fetch, locals, params }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const name = formData.get('name') as string;
		const description = formData.get('description') as string;

		if (!name?.trim()) return fail(400, { name, description, error: '이름을 입력하세요.' });

		try {
			const data = await graphqlRequest<{
				createProject: { project: { id: string } };
			}>(
				fetch,
				CREATE_PROJECT_MUTATION,
				{
					input: {
						organizationId: params.orgId,
						name: name.trim(),
						description: description?.trim() || ''
					}
				},
				accessToken
			);
			redirect(303, `/orgs/${params.orgId}/projects/${data.createProject.project.id}`);
		} catch (e) {
			if (e instanceof Response || (e as { status?: number }).status === 303) throw e;
			return fail(400, {
				name,
				description,
				error: e instanceof Error ? e.message : '프로젝트 생성에 실패했습니다.'
			});
		}
	}
};
