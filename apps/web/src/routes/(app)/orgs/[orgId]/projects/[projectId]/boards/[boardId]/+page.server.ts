import { fail } from '@sveltejs/kit';
import { graphqlRequest } from '$lib/server/graphql';
import { BOARD_QUERY } from '$lib/graphql/queries/board';
import {
	UPDATE_BOARD_MUTATION,
	DELETE_BOARD_MUTATION,
	CREATE_TASK_GROUP_MUTATION,
	UPDATE_TASK_GROUP_MUTATION,
	DELETE_TASK_GROUP_MUTATION,
	REORDER_TASK_GROUPS_MUTATION
} from '$lib/graphql/mutations/board';
import {
	CREATE_TASK_MUTATION,
	UPDATE_TASK_MUTATION,
	DELETE_TASK_MUTATION,
	MOVE_TASK_MUTATION,
	REORDER_TASKS_MUTATION,
	ASSIGN_TASK_MUTATION
} from '$lib/graphql/mutations/task';
import type { PageServerLoad, Actions } from './$types';
import type { Board } from '$lib/types';

export const load: PageServerLoad = async ({ params, fetch, parent }) => {
	const { accessToken } = await parent();

	const data = await graphqlRequest<{ board: Board }>(
		fetch,
		BOARD_QUERY,
		{ id: params.boardId },
		accessToken
	);

	return { board: data.board };
};

export const actions: Actions = {
	updateBoard: async ({ request, fetch, locals, params }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const name = formData.get('name') as string;
		const description = formData.get('description') as string;

		if (!name?.trim()) return fail(400, { error: '이름을 입력하세요.' });

		try {
			await graphqlRequest(
				fetch,
				UPDATE_BOARD_MUTATION,
				{ input: { boardId: params.boardId, name: name.trim(), description: description?.trim() || '' } },
				accessToken
			);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '보드 수정에 실패했습니다.' });
		}
	},

	deleteBoard: async ({ fetch, locals, params }) => {
		const accessToken = locals.accessToken;

		try {
			await graphqlRequest(fetch, DELETE_BOARD_MUTATION, { id: params.boardId }, accessToken);
			return { deleted: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '보드 삭제에 실패했습니다.' });
		}
	},

	createTaskGroup: async ({ request, fetch, locals, params }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const name = formData.get('name') as string;

		if (!name?.trim()) return fail(400, { error: '이름을 입력하세요.' });

		try {
			await graphqlRequest(
				fetch,
				CREATE_TASK_GROUP_MUTATION,
				{ input: { boardId: params.boardId, name: name.trim() } },
				accessToken
			);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '컬럼 생성에 실패했습니다.' });
		}
	},

	updateTaskGroup: async ({ request, fetch, locals, params }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const taskGroupId = formData.get('task_group_id') as string;
		const name = formData.get('name') as string;

		if (!name?.trim()) return fail(400, { error: '이름을 입력하세요.' });

		try {
			await graphqlRequest(
				fetch,
				UPDATE_TASK_GROUP_MUTATION,
				{ input: { boardId: params.boardId, taskGroupId, name: name.trim() } },
				accessToken
			);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '컬럼 수정에 실패했습니다.' });
		}
	},

	deleteTaskGroup: async ({ request, fetch, locals, params }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const taskGroupId = formData.get('task_group_id') as string;

		try {
			await graphqlRequest(
				fetch,
				DELETE_TASK_GROUP_MUTATION,
				{ input: { boardId: params.boardId, taskGroupId } },
				accessToken
			);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '컬럼 삭제에 실패했습니다.' });
		}
	},

	reorderTaskGroups: async ({ request, fetch, locals, params }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		let taskGroupIds: string[];
		try {
			taskGroupIds = JSON.parse(formData.get('task_group_ids') as string);
		} catch {
			return fail(400, { error: '잘못된 요청 데이터입니다.' });
		}

		try {
			await graphqlRequest(
				fetch,
				REORDER_TASK_GROUPS_MUTATION,
				{ input: { boardId: params.boardId, taskGroupIds } },
				accessToken
			);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '순서 변경에 실패했습니다.' });
		}
	},

	createTask: async ({ request, fetch, locals }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const taskGroupId = formData.get('task_group_id') as string;
		const title = formData.get('title') as string;
		const description = formData.get('description') as string;
		const status = formData.get('status') as string;
		const priority = formData.get('priority') as string;
		const assigneeId = formData.get('assignee_id') as string;
		const dueDate = formData.get('due_date') as string;

		if (!title?.trim()) return fail(400, { error: '제목을 입력하세요.' });

		const input: Record<string, unknown> = {
			taskGroupId,
			title: title.trim()
		};
		if (description?.trim()) input.description = description.trim();
		if (status) input.status = status;
		if (priority) input.priority = priority;
		if (assigneeId) input.assigneeId = assigneeId;
		if (dueDate) input.dueDate = dueDate;

		try {
			await graphqlRequest(fetch, CREATE_TASK_MUTATION, { input }, accessToken);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '태스크 생성에 실패했습니다.' });
		}
	},

	updateTask: async ({ request, fetch, locals }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const taskId = formData.get('task_id') as string;
		const title = formData.get('title') as string;
		const description = formData.get('description') as string;
		const status = formData.get('status') as string;
		const priority = formData.get('priority') as string;
		const dueDate = formData.get('due_date') as string;

		const input: Record<string, unknown> = { taskId };
		if (title !== null) input.title = title;
		if (description !== null) input.description = description;
		if (status) input.status = status;
		if (priority) input.priority = priority;
		if (dueDate !== null) input.dueDate = dueDate || null;

		try {
			await graphqlRequest(fetch, UPDATE_TASK_MUTATION, { input }, accessToken);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '태스크 수정에 실패했습니다.' });
		}
	},

	deleteTask: async ({ request, fetch, locals }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const taskId = formData.get('task_id') as string;

		try {
			await graphqlRequest(fetch, DELETE_TASK_MUTATION, { id: taskId }, accessToken);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '태스크 삭제에 실패했습니다.' });
		}
	},

	moveTask: async ({ request, fetch, locals }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const taskId = formData.get('task_id') as string;
		const targetTaskGroupId = formData.get('target_task_group_id') as string;
		const position = formData.get('position') as string;

		const input: Record<string, unknown> = { taskId, targetTaskGroupId };
		if (position) input.position = parseInt(position);

		try {
			await graphqlRequest(fetch, MOVE_TASK_MUTATION, { input }, accessToken);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '태스크 이동에 실패했습니다.' });
		}
	},

	reorderTasks: async ({ request, fetch, locals }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const taskGroupId = formData.get('task_group_id') as string;
		let taskIds: string[];
		try {
			taskIds = JSON.parse(formData.get('task_ids') as string);
		} catch {
			return fail(400, { error: '잘못된 요청 데이터입니다.' });
		}

		try {
			await graphqlRequest(
				fetch,
				REORDER_TASKS_MUTATION,
				{ input: { taskGroupId, taskIds } },
				accessToken
			);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '순서 변경에 실패했습니다.' });
		}
	},

	assignTask: async ({ request, fetch, locals }) => {
		const accessToken = locals.accessToken;
		const formData = await request.formData();
		const taskId = formData.get('task_id') as string;
		const assigneeId = formData.get('assignee_id') as string;

		try {
			await graphqlRequest(
				fetch,
				ASSIGN_TASK_MUTATION,
				{ input: { taskId, assigneeId: assigneeId || null } },
				accessToken
			);
			return { success: true };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '담당자 변경에 실패했습니다.' });
		}
	}
};
