import { graphqlRequest } from '$lib/server/graphql';
import { PROJECT_QUERY } from '$lib/graphql/queries/project';
import { BOARDS_QUERY } from '$lib/graphql/queries/board';
import type { LayoutServerLoad } from './$types';
import type { Project, Board } from '$lib/types';

export const load: LayoutServerLoad = async ({ params, fetch, parent }) => {
	const { accessToken } = await parent();

	const [projectData, boardsData] = await Promise.all([
		graphqlRequest<{ project: Project }>(
			fetch,
			PROJECT_QUERY,
			{ id: params.projectId },
			accessToken
		),
		graphqlRequest<{ boards: Board[] }>(
			fetch,
			BOARDS_QUERY,
			{ projectId: params.projectId },
			accessToken
		)
	]);

	return {
		project: projectData.project,
		boards: boardsData.boards
	};
};
