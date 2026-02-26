import { error } from '@sveltejs/kit';
import { graphqlRequest } from '$lib/server/graphql';
import { ORGANIZATION_QUERY } from '$lib/graphql/queries/organization';
import type { LayoutServerLoad } from './$types';
import type { Organization, OrgRole } from '$lib/types';

export const load: LayoutServerLoad = async ({ params, fetch, parent }) => {
	const { accessToken, user } = await parent();

	const data = await graphqlRequest<{ organization: Organization }>(
		fetch,
		ORGANIZATION_QUERY,
		{ id: params.orgId },
		accessToken
	);

	const org = data.organization;
	const membership = org.members.find((m) => m.user.id === user.id);

	if (!membership) {
		error(403, '이 Organization에 접근할 권한이 없습니다.');
	}

	const userRole: OrgRole = membership.role;
	const isAdmin = userRole === 'ADMIN' || userRole === 'OWNER';
	const isOwner = userRole === 'OWNER';

	return { org, userRole, isAdmin, isOwner };
};
