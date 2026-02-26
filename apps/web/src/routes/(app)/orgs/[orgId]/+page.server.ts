import { graphqlRequest } from '$lib/server/graphql';
import { PROJECTS_QUERY } from '$lib/graphql/queries/project';
import type { PageServerLoad } from './$types';
import type { Project } from '$lib/types';

export const load: PageServerLoad = async ({ params, fetch, parent }) => {
	const { accessToken } = await parent();

	const data = await graphqlRequest<{ projects: Project[] }>(
		fetch,
		PROJECTS_QUERY,
		{ organizationId: params.orgId },
		accessToken
	);

	return { projects: data.projects };
};
