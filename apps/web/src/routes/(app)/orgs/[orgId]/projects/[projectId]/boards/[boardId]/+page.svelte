<script lang="ts">
	import { enhance, deserialize } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import type { PageProps } from './$types';
	import type { Task } from '$lib/types';
	import KanbanBoard from '$lib/components/board/KanbanBoard.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import Textarea from '$lib/components/ui/Textarea.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Avatar from '$lib/components/ui/Avatar.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
	import SearchInput from '$lib/components/ui/SearchInput.svelte';
	import { toastStore } from '$lib/stores/toast.svelte';

	let { data, form }: PageProps = $props();

	// 검색 상태
	let searchQuery = $state('');
	let filteredBoard = $derived.by(() => {
		if (!searchQuery.trim()) return data.board;
		const q = searchQuery.toLowerCase();
		return {
			...data.board,
			taskGroups: data.board.taskGroups.map((group) => ({
				...group,
				tasks: group.tasks.filter(
					(task) =>
						task.title.toLowerCase().includes(q) ||
						task.description?.toLowerCase().includes(q) ||
						task.labels.some((l) => l.name.toLowerCase().includes(q))
				)
			}))
		};
	});

	// 보드 이름 인라인 수정 상태
	let isEditingName = $state(false);
	let editName = $state('');

	// 모달 상태
	let showTaskCreate = $state(false);
	let createTaskGroupId = $state('');
	let createDefaultStatus = $derived.by(() => {
		const group = data.board.taskGroups.find((g) => g.id === createTaskGroupId);
		if (group) {
			return columnNameToStatus[group.name.toUpperCase()] || 'TODO';
		}
		return 'TODO';
	});
	let showTaskDetail = $state(false);
	let selectedTask: Task | null = $state(null);
	let showColumnCreate = $state(false);
	let showColumnEdit = $state(false);
	let editColumnId = $state('');
	let editColumnName = $state('');

	// 삭제 확인 다이얼로그 상태
	let showDeleteColumnConfirm = $state(false);
	let deleteColumnId = $state('');
	let deletingColumn = $state(false);
	let showDeleteTaskConfirm = $state(false);
	let deletingTask = $state(false);

	const statusOptions = [
		{ value: 'TODO', label: 'To Do' },
		{ value: 'IN_PROGRESS', label: 'In Progress' },
		{ value: 'IN_REVIEW', label: 'In Review' },
		{ value: 'DONE', label: 'Done' }
	];

	const priorityOptions = [
		{ value: 'LOW', label: 'Low' },
		{ value: 'MEDIUM', label: 'Medium' },
		{ value: 'HIGH', label: 'High' },
		{ value: 'URGENT', label: 'Urgent' }
	];

	const statusLabels: Record<string, string> = {
		TODO: 'To Do',
		IN_PROGRESS: 'In Progress',
		IN_REVIEW: 'In Review',
		DONE: 'Done'
	};

	const priorityLabels: Record<string, string> = {
		LOW: 'Low',
		MEDIUM: 'Medium',
		HIGH: 'High',
		URGENT: 'Urgent'
	};

	async function fetchAction(action: string, formData: FormData): Promise<boolean> {
		const response = await fetch(`?/${action}`, { method: 'POST', body: formData });
		const result = deserialize(await response.text());
		if (result.type === 'failure') {
			toastStore.error((result.data?.error as string) || '요청에 실패했습니다.');
			return false;
		}
		return true;
	}

	function handleTaskClick(task: Task) {
		selectedTask = task;
		showTaskDetail = true;
	}

	function handleAddTask(taskGroupId: string) {
		createTaskGroupId = taskGroupId;
		showTaskCreate = true;
	}

	function handleAddColumn() {
		showColumnCreate = true;
	}

	function handleEditColumnName(taskGroupId: string, currentName: string) {
		editColumnId = taskGroupId;
		editColumnName = currentName;
		showColumnEdit = true;
	}

	function handleDeleteColumn(taskGroupId: string) {
		deleteColumnId = taskGroupId;
		showDeleteColumnConfirm = true;
	}

	async function confirmDeleteColumn() {
		deletingColumn = true;
		const formData = new FormData();
		formData.set('task_group_id', deleteColumnId);

		const ok = await fetchAction('deleteTaskGroup', formData);
		await invalidateAll();
		deletingColumn = false;
		showDeleteColumnConfirm = false;
		if (ok) toastStore.success('컬럼이 삭제되었습니다.');
	}

	const columnNameToStatus: Record<string, string> = {
		'TO DO': 'TODO',
		'IN PROGRESS': 'IN_PROGRESS',
		'IN REVIEW': 'IN_REVIEW',
		'DONE': 'DONE'
	};

	const statusToColumnName = Object.fromEntries(
		Object.entries(columnNameToStatus).map(([k, v]) => [v, k])
	);

	async function handleMoveTask(taskId: string, targetGroupId: string, position?: number) {
		const formData = new FormData();
		formData.set('task_id', taskId);
		formData.set('target_task_group_id', targetGroupId);
		if (position !== undefined) formData.set('position', String(position));

		const ok = await fetchAction('moveTask', formData);
		if (!ok) return;

		// 컬럼 이름에 대응하는 status가 있으면 자동 업데이트
		const targetGroup = data.board.taskGroups.find((g) => g.id === targetGroupId);
		if (targetGroup) {
			const newStatus = columnNameToStatus[targetGroup.name.toUpperCase()];
			if (newStatus) {
				const statusForm = new FormData();
				statusForm.set('task_id', taskId);
				statusForm.set('status', newStatus);
				await fetchAction('updateTask', statusForm);
			}
		}

		await invalidateAll();
	}

	async function handleReorderTasks(taskGroupId: string, taskIds: string[]) {
		const formData = new FormData();
		formData.set('task_group_id', taskGroupId);
		formData.set('task_ids', JSON.stringify(taskIds));

		await fetchAction('reorderTasks', formData);
		await invalidateAll();
	}

	async function handleReorderTaskGroups(taskGroupIds: string[]) {
		const formData = new FormData();
		formData.set('task_group_ids', JSON.stringify(taskGroupIds));

		await fetchAction('reorderTaskGroups', formData);
		await invalidateAll();
	}

	function handleDeleteTask() {
		showDeleteTaskConfirm = true;
	}

	async function confirmDeleteTask() {
		if (!selectedTask) return;
		deletingTask = true;
		const formData = new FormData();
		formData.set('task_id', selectedTask.id);

		const ok = await fetchAction('deleteTask', formData);
		deletingTask = false;
		showDeleteTaskConfirm = false;
		closeAndRefresh();
		if (ok) toastStore.success('태스크가 삭제되었습니다.');
	}

	function closeAndRefresh() {
		showTaskCreate = false;
		showTaskDetail = false;
		showColumnCreate = false;
		showColumnEdit = false;
		showDeleteTaskConfirm = false;
		selectedTask = null;
		invalidateAll();
	}
</script>

<svelte:head>
	<title>{data.board.name} - TaskFlow</title>
</svelte:head>

{#if form?.error}
	<div class="mb-4"><Alert variant="error">{form.error}</Alert></div>
{/if}

<div class="mb-4 flex items-center justify-between">
	{#if isEditingName}
		<form
			method="POST"
			action="?/updateBoard"
			use:enhance={() => {
				return async ({ update }) => {
					await update();
					isEditingName = false;
					invalidateAll();
				};
			}}
			class="flex items-center gap-2"
		>
			<input
				type="text"
				name="name"
				value={editName}
				class="rounded-md border border-surface-300 px-2 py-1 text-lg font-semibold tracking-tight text-surface-900 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
				autofocus
				onkeydown={(e) => { if (e.key === 'Escape') isEditingName = false; }}
			/>
			<button
				type="submit"
				class="rounded-md p-1 text-primary-600 transition-colors hover:bg-primary-50"
				title="저장"
			>
				<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
				</svg>
			</button>
			<button
				type="button"
				class="rounded-md p-1 text-surface-400 transition-colors hover:bg-surface-200 hover:text-surface-600"
				onclick={() => (isEditingName = false)}
				title="취소"
			>
				<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		</form>
	{:else}
		<div class="flex items-center gap-1.5">
			<h2 class="text-lg font-semibold tracking-tight text-surface-900">{data.board.name}</h2>
			<button
				class="rounded-md p-1 text-surface-400 transition-colors hover:bg-surface-200 hover:text-surface-600"
				onclick={() => { editName = data.board.name; isEditingName = true; }}
				title="보드 이름 수정"
			>
				<svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
				</svg>
			</button>
		</div>
	{/if}
	<div class="w-64">
		<SearchInput
			placeholder="태스크 검색..."
			onsearch={(q) => (searchQuery = q)}
		/>
	</div>
</div>

<KanbanBoard
	board={filteredBoard}
	isAdmin={data.isAdmin}
	onTaskClick={handleTaskClick}
	onAddTask={handleAddTask}
	onAddColumn={handleAddColumn}
	onEditColumnName={handleEditColumnName}
	onDeleteColumn={handleDeleteColumn}
	onMoveTask={handleMoveTask}
	onReorderTasks={handleReorderTasks}
	onReorderTaskGroups={handleReorderTaskGroups}
/>

<!-- 태스크 생성 모달 -->
<Modal open={showTaskCreate} onclose={() => (showTaskCreate = false)} title="새 태스크">
	<form
		method="POST"
		action="?/createTask"
		use:enhance={() => {
			return async ({ update }) => {
				await update();
				closeAndRefresh();
			};
		}}
		class="space-y-4"
	>
		<input type="hidden" name="task_group_id" value={createTaskGroupId} />
		<Input id="task-title" name="title" label="제목" required placeholder="태스크 제목" />
		<Textarea
			id="task-description"
			name="description"
			label="설명"
			rows={3}
			placeholder="태스크 설명 (선택)"
		/>
		<div class="grid grid-cols-2 gap-4">
			<Select id="task-status" name="status" label="상태" options={statusOptions} value={createDefaultStatus} />
			<Select id="task-priority" name="priority" label="우선순위" options={priorityOptions} />
		</div>
		<Select
			id="task-assignee"
			name="assignee_id"
			label="담당자"
			options={[
				{ value: '', label: '미할당' },
				...data.project.members.map((m) => ({
					value: m.user.id,
					label: `${m.user.firstName} ${m.user.lastName || m.user.username}`
				}))
			]}
		/>
		<Input id="task-due-date" name="due_date" type="date" label="마감일" />
		<div class="flex justify-end gap-2">
			<Button type="button" variant="secondary" onclick={() => (showTaskCreate = false)}>
				취소
			</Button>
			<Button type="submit">생성</Button>
		</div>
	</form>
</Modal>

<!-- 태스크 상세 모달 -->
<Modal
	open={showTaskDetail}
	onclose={() => { showTaskDetail = false; selectedTask = null; }}
	title={selectedTask?.title || ''}
	size="lg"
>
	{#if selectedTask}
		<div class="space-y-4">
			<div class="flex gap-2">
				<Badge variant={selectedTask.status === 'DONE' ? 'success' : selectedTask.status === 'IN_PROGRESS' ? 'info' : 'default'} dot>
					{statusLabels[selectedTask.status]}
				</Badge>
				<Badge>{priorityLabels[selectedTask.priority]}</Badge>
			</div>

			{#if selectedTask.assignee}
				<div class="flex items-center gap-2">
					<span class="text-sm text-surface-500">담당자:</span>
					<Avatar
						src={selectedTask.assignee.profileImage}
						alt="{selectedTask.assignee.firstName} {selectedTask.assignee.lastName}"
						size="sm"
					/>
					<span class="text-sm text-surface-900">
						{selectedTask.assignee.firstName} {selectedTask.assignee.lastName || selectedTask.assignee.username}
					</span>
				</div>
			{/if}

			{#if selectedTask.dueDate}
				<p class="text-sm text-surface-500">
					마감일: {new Date(selectedTask.dueDate).toLocaleDateString('ko-KR')}
				</p>
			{/if}

			{#if selectedTask.labels.length > 0}
				<div class="flex flex-wrap gap-1">
					{#each selectedTask.labels as label}
						<span
							class="rounded-md px-2 py-0.5 text-xs font-medium text-white"
							style="background-color: {label.color}"
						>
							{label.name}
						</span>
					{/each}
				</div>
			{/if}

			<!-- 인라인 수정 폼 -->
			<form
				method="POST"
				action="?/updateTask"
				use:enhance={({ formData }) => {
					const newStatus = formData.get('status') as string;
					const taskId = selectedTask?.id;
					const currentStatus = selectedTask?.status;
					return async ({ update }) => {
						await update();
						// 상태가 변경되었고 대응하는 컬럼이 있으면 자동 이동
						if (taskId && newStatus && currentStatus && newStatus !== currentStatus) {
							const targetColumnName = statusToColumnName[newStatus];
							if (targetColumnName) {
								const targetGroup = data.board.taskGroups.find(
									(g) => g.name.toUpperCase() === targetColumnName
								);
								const currentGroup = data.board.taskGroups.find((g) =>
									g.tasks.some((t) => t.id === taskId)
								);
								if (targetGroup && currentGroup && targetGroup.id !== currentGroup.id) {
									const fd = new FormData();
									fd.set('task_id', taskId);
									fd.set('target_task_group_id', targetGroup.id);
									await fetch('?/moveTask', { method: 'POST', body: fd });
								}
							}
						}
						closeAndRefresh();
					};
				}}
				class="space-y-4 border-t border-surface-100 pt-4"
			>
				<input type="hidden" name="task_id" value={selectedTask.id} />
				<Input id="edit-title" name="title" label="제목" value={selectedTask.title} required />
				<Textarea
					id="edit-description"
					name="description"
					label="설명"
					rows={3}
					value={selectedTask.description || ''}
				/>
				<div class="grid grid-cols-2 gap-4">
					<Select id="edit-status" name="status" label="상태" options={statusOptions} value={selectedTask.status} />
					<Select id="edit-priority" name="priority" label="우선순위" options={priorityOptions} value={selectedTask.priority} />
				</div>
				<Input id="edit-due-date" name="due_date" type="date" label="마감일" value={selectedTask.dueDate || ''} />
				<div class="flex justify-end gap-2">
					<Button type="button" variant="secondary" onclick={() => { showTaskDetail = false; selectedTask = null; }}>
						취소
					</Button>
					<Button type="submit">저장</Button>
				</div>
			</form>

			<!-- 삭제 버튼 -->
			{#if data.isAdmin || selectedTask.createdBy.id === data.user.id}
				<div class="border-t border-surface-100 pt-4">
					<Button type="button" variant="danger" size="sm" onclick={handleDeleteTask}>삭제</Button>
				</div>
			{/if}

			<!-- 담당자 변경 -->
			<form
				method="POST"
				action="?/assignTask"
				use:enhance={() => {
					return async ({ update }) => {
						await update();
						closeAndRefresh();
					};
				}}
				class="border-t border-surface-100 pt-4"
			>
				<input type="hidden" name="task_id" value={selectedTask.id} />
				<Select
					id="assign-task"
					name="assignee_id"
					label="담당자 변경"
					options={[
						{ value: '', label: '미할당' },
						...data.project.members.map((m) => ({
							value: m.user.id,
							label: `${m.user.firstName} ${m.user.lastName || m.user.username}`
						}))
					]}
					value={selectedTask.assignee?.id || ''}
				/>
				<Button type="submit" size="sm" class="mt-2">담당자 변경</Button>
			</form>
		</div>
	{/if}
</Modal>

<!-- 컬럼 생성 모달 -->
<Modal open={showColumnCreate} onclose={() => (showColumnCreate = false)} title="컬럼 추가" size="sm">
	<form
		method="POST"
		action="?/createTaskGroup"
		use:enhance={() => {
			return async ({ update }) => {
				await update();
				closeAndRefresh();
			};
		}}
		class="space-y-4"
	>
		<Input id="column-name" name="name" label="컬럼 이름" required placeholder="예: In Progress" />
		<div class="flex justify-end gap-2">
			<Button type="button" variant="secondary" onclick={() => (showColumnCreate = false)}>
				취소
			</Button>
			<Button type="submit">생성</Button>
		</div>
	</form>
</Modal>

<!-- 컬럼 이름 수정 모달 -->
<Modal open={showColumnEdit} onclose={() => (showColumnEdit = false)} title="컬럼 이름 수정" size="sm">
	<form
		method="POST"
		action="?/updateTaskGroup"
		use:enhance={() => {
			return async ({ update }) => {
				await update();
				closeAndRefresh();
				toastStore.success('컬럼 이름이 수정되었습니다.');
			};
		}}
		class="space-y-4"
	>
		<input type="hidden" name="task_group_id" value={editColumnId} />
		<Input id="edit-column-name" name="name" label="컬럼 이름" value={editColumnName} required />
		<div class="flex justify-end gap-2">
			<Button type="button" variant="secondary" onclick={() => (showColumnEdit = false)}>
				취소
			</Button>
			<Button type="submit">저장</Button>
		</div>
	</form>
</Modal>

<!-- 컬럼 삭제 확인 다이얼로그 -->
<ConfirmDialog
	open={showDeleteColumnConfirm}
	title="컬럼 삭제"
	description="이 컬럼을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다."
	confirmLabel="삭제"
	variant="danger"
	loading={deletingColumn}
	onconfirm={confirmDeleteColumn}
	oncancel={() => (showDeleteColumnConfirm = false)}
/>

<!-- 태스크 삭제 확인 다이얼로그 -->
<ConfirmDialog
	open={showDeleteTaskConfirm}
	title="태스크 삭제"
	description="이 태스크를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다."
	confirmLabel="삭제"
	variant="danger"
	loading={deletingTask}
	onconfirm={confirmDeleteTask}
	oncancel={() => (showDeleteTaskConfirm = false)}
/>
