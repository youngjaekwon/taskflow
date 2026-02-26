import { fail, redirect } from '@sveltejs/kit';
import { graphqlRequest } from '$lib/server/graphql';
import { CREATE_ORGANIZATION_MUTATION } from '$lib/graphql/mutations/organization';
import type { Actions } from './$types';

export const actions: Actions = {
	default: async ({ request, fetch, locals }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const name = formData.get('name') as string;
		const description = formData.get('description') as string;

		if (!name?.trim()) return fail(400, { name, description, error: '이름을 입력하세요.' });

		try {
			const data = await graphqlRequest<{
				createOrganization: { organization: { id: string } };
			}>(
				fetch,
				CREATE_ORGANIZATION_MUTATION,
				{ input: { name: name.trim(), description: description?.trim() || '' } },
				accessToken
			);
			redirect(303, `/orgs/${data.createOrganization.organization.id}`);
		} catch (e) {
			if (e instanceof Response || (e as { status?: number }).status === 303) throw e;
			return fail(400, {
				name,
				description,
				error: e instanceof Error ? e.message : 'Organization 생성에 실패했습니다.'
			});
		}
	}
};
