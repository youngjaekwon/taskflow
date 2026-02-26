import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, parent }) => {
	const { boards } = await parent();

	if (boards.length > 0) {
		redirect(
			303,
			`/orgs/${params.orgId}/projects/${params.projectId}/boards/${boards[0].id}`
		);
	}

	redirect(303, `/orgs/${params.orgId}/projects/${params.projectId}/settings`);
};
