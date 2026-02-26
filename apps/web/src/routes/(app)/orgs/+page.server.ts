import { graphqlRequest } from '$lib/server/graphql';
import { MY_ORGANIZATIONS_QUERY } from '$lib/graphql/queries/user';
import type { PageServerLoad } from './$types';
import type { Organization } from '$lib/types';

export const load: PageServerLoad = async ({ fetch, parent }) => {
	const { accessToken } = await parent();
	const data = await graphqlRequest<{ myOrganizations: Organization[] }>(
		fetch,
		MY_ORGANIZATIONS_QUERY,
		{},
		accessToken
	);

	return { organizations: data.myOrganizations };
};
