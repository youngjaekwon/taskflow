<script lang="ts">
	import type { TaskGroup, Task } from '$lib/types';
	import TaskCard from './TaskCard.svelte';

	interface Props {
		taskGroup: TaskGroup;
		isAdmin: boolean;
		onTaskClick: (task: Task) => void;
		onAddTask: (taskGroupId: string) => void;
		onEditName?: (taskGroupId: string, currentName: string) => void;
		onDeleteGroup?: (taskGroupId: string) => void;
		ondragover?: (e: DragEvent) => void;
		ondrop?: (e: DragEvent) => void;
		onTaskDragStart?: (e: DragEvent, task: Task) => void;
		selectedTaskId?: string | null;
		isMoving?: boolean;
		onTaskSelect?: (taskId: string) => void;
		// D&D 시각적 피드백
		dropIndex?: number | null;
		isDropTarget?: boolean;
		isDraggingTask?: boolean;
		draggedTaskId?: string | null;
		// 컬럼 D&D (ADMIN 전용)
		columnDraggable?: boolean;
		onColumnDragStart?: (e: DragEvent) => void;
		isDraggingColumn?: boolean;
		columnDropIndicator?: 'left' | 'right' | null;
	}

	let {
		taskGroup,
		isAdmin,
		onTaskClick,
		onAddTask,
		onEditName,
		onDeleteGroup,
		ondragover,
		ondrop,
		onTaskDragStart,
		selectedTaskId = null,
		isMoving = false,
		onTaskSelect,
		dropIndex = null,
		isDropTarget = false,
		isDraggingTask = false,
		draggedTaskId = null,
		columnDraggable = false,
		onColumnDragStart,
		isDraggingColumn = false,
		columnDropIndicator = null
	}: Props = $props();

	let sortedTasks = $derived(
		[...taskGroup.tasks].sort((a, b) => a.position - b.position)
	);

	let hasSelectedTask = $derived(
		sortedTasks.some((t) => t.id === selectedTaskId)
	);

	const columnColors = [
		'bg-brand-500',
		'bg-success-500',
		'bg-warning-500',
		'bg-danger-500',
		'bg-info-500'
	];

	function getColumnDotColor(name: string): string {
		let hash = 0;
		for (let i = 0; i < name.length; i++) {
			hash = name.charCodeAt(i) + ((hash << 5) - hash);
		}
		return columnColors[Math.abs(hash) % columnColors.length];
	}
</script>

<div class="relative flex shrink-0 {isDraggingColumn ? 'opacity-50' : ''}">
	<!-- 컬럼 왼쪽 삽입 인디케이터 -->
	{#if columnDropIndicator === 'left'}
		<div class="absolute -left-1.5 top-0 bottom-0 w-1 rounded-full bg-brand-500 z-10"></div>
	{/if}

	<div
		class="flex h-full w-72 shrink-0 flex-col rounded-xl bg-surface-100/50 transition-all duration-150 {isMoving && hasSelectedTask ? 'ring-2 ring-brand-500/30' : ''} {isDropTarget && isDraggingTask ? 'ring-2 ring-brand-500/20 bg-brand-50/30' : ''}"
		ondragover={(e) => { e.preventDefault(); ondragover?.(e); }}
		ondrop={ondrop}
		role="list"
		aria-label="{taskGroup.name} 컬럼"
	>
		<!-- 컬럼 헤더 -->
		<div class="flex items-center justify-between px-3 py-3">
			<div class="flex items-center gap-2">
				{#if columnDraggable}
					<!-- svelte-ignore a11y_no_static_element_interactions -->
					<div
						class="cursor-grab active:cursor-grabbing text-surface-300 hover:text-surface-500 transition-colors"
						draggable="true"
						ondragstart={onColumnDragStart}
					>
						<svg class="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
							<circle cx="9" cy="5" r="1.5" />
							<circle cx="15" cy="5" r="1.5" />
							<circle cx="9" cy="12" r="1.5" />
							<circle cx="15" cy="12" r="1.5" />
							<circle cx="9" cy="19" r="1.5" />
							<circle cx="15" cy="19" r="1.5" />
						</svg>
					</div>
				{/if}
				<span class="h-2 w-2 rounded-full {getColumnDotColor(taskGroup.name)}"></span>
				<h3 class="text-xs font-semibold uppercase tracking-wider text-surface-500">{taskGroup.name}</h3>
				<span class="inline-flex h-5 min-w-5 items-center justify-center rounded-md bg-surface-200/80 px-1.5 text-xs font-medium text-surface-500">{taskGroup.tasks.length}</span>
			</div>
			{#if isAdmin}
				<div class="flex gap-0.5">
					<button
						class="rounded-md p-1 text-surface-400 transition-colors hover:bg-surface-200 hover:text-surface-600"
						onclick={() => onEditName?.(taskGroup.id, taskGroup.name)}
						title="이름 수정"
					>
						<svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
						</svg>
					</button>
					{#if taskGroup.tasks.length === 0}
						<button
							class="rounded-md p-1 text-surface-400 transition-colors hover:bg-danger-50 hover:text-danger-600"
							onclick={() => onDeleteGroup?.(taskGroup.id)}
							title="삭제"
						>
							<svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
							</svg>
						</button>
					{/if}
				</div>
			{/if}
		</div>

		<!-- 태스크 목록 -->
		<div class="flex-1 space-y-2 overflow-y-auto px-2 pb-2 pt-1">
			{#each sortedTasks as task, index (task.id)}
				<div role="listitem">
					{#if dropIndex === index && isDropTarget}
						<div class="h-1 rounded-full bg-brand-500 mx-1 my-1 transition-all"></div>
					{/if}
					<TaskCard
						{task}
						onclick={() => onTaskClick(task)}
						draggable={true}
						ondragstart={(e) => onTaskDragStart?.(e, task)}
						selected={selectedTaskId === task.id}
						moving={isMoving && selectedTaskId === task.id}
						isDragging={draggedTaskId === task.id}
						onfocus={() => onTaskSelect?.(task.id)}
					/>
				</div>
			{/each}
			{#if dropIndex === sortedTasks.length && isDropTarget}
				<div class="h-1 rounded-full bg-brand-500 mx-1 my-1 transition-all"></div>
			{/if}
		</div>

		<!-- 태스크 추가 버튼 -->
		<div class="p-2">
			<button
				class="flex w-full items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-surface-400 transition-colors hover:bg-surface-200/60 hover:text-surface-600"
				onclick={() => onAddTask(taskGroup.id)}
			>
				<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
				</svg>
				태스크 추가
			</button>
		</div>
	</div>

	<!-- 컬럼 오른쪽 삽입 인디케이터 -->
	{#if columnDropIndicator === 'right'}
		<div class="absolute -right-1.5 top-0 bottom-0 w-1 rounded-full bg-brand-500 z-10"></div>
	{/if}
</div>
