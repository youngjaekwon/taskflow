<script lang="ts">
	import type { Board, Task, TaskGroup } from '$lib/types';
	import { announcer } from '$lib/stores/announcer.svelte';
	import TaskGroupColumn from './TaskGroupColumn.svelte';

	interface Props {
		board: Board;
		isAdmin: boolean;
		onTaskClick: (task: Task) => void;
		onAddTask: (taskGroupId: string) => void;
		onAddColumn?: () => void;
		onEditColumnName?: (taskGroupId: string, currentName: string) => void;
		onDeleteColumn?: (taskGroupId: string) => void;
		onMoveTask?: (taskId: string, targetGroupId: string, position?: number) => void;
		onReorderTasks?: (taskGroupId: string, taskIds: string[]) => void;
		onReorderTaskGroups?: (taskGroupIds: string[]) => void;
	}

	let {
		board,
		isAdmin,
		onTaskClick,
		onAddTask,
		onAddColumn,
		onEditColumnName,
		onDeleteColumn,
		onMoveTask,
		onReorderTasks,
		onReorderTaskGroups
	}: Props = $props();

	let sortedGroups = $derived(
		[...board.taskGroups].sort((a, b) => a.position - b.position)
	);

	// 태스크 D&D 상태
	let draggedTask: Task | null = $state(null);
	let dragSourceGroupId: string | null = $state(null);
	let dropTargetGroupId: string | null = $state(null);
	let dropIndex: number | null = $state(null);

	// 컬럼 D&D 상태 (ADMIN 전용)
	let draggedGroupId: string | null = $state(null);
	let columnDropIndex: number | null = $state(null);

	// 키보드 내비게이션 상태
	let selectedTaskId: string | null = $state(null);
	let isMoving = $state(false);

	function findTaskGroup(taskId: string): { group: TaskGroup; taskIndex: number; groupIndex: number } | null {
		for (let gi = 0; gi < sortedGroups.length; gi++) {
			const group = sortedGroups[gi];
			const sorted = [...group.tasks].sort((a, b) => a.position - b.position);
			const ti = sorted.findIndex((t) => t.id === taskId);
			if (ti !== -1) return { group, taskIndex: ti, groupIndex: gi };
		}
		return null;
	}

	function handleKeyboardNavigation(e: KeyboardEvent) {
		if (!selectedTaskId) return;
		const loc = findTaskGroup(selectedTaskId);
		if (!loc) return;

		const { group, taskIndex, groupIndex } = loc;
		const sortedTasks = [...group.tasks].sort((a, b) => a.position - b.position);

		if (e.key === ' ' || e.key === 'Enter') {
			e.preventDefault();
			if (isMoving) {
				isMoving = false;
				announcer.announce(`${sortedTasks[taskIndex]?.title} 이동 완료`);
			} else {
				isMoving = true;
				announcer.announce(`${sortedTasks[taskIndex]?.title} 선택됨. 화살표 키로 이동하세요.`);
			}
			return;
		}

		if (e.key === 'Escape') {
			e.preventDefault();
			if (isMoving) {
				isMoving = false;
				announcer.announce('이동 취소');
			} else {
				selectedTaskId = null;
			}
			return;
		}

		if (isMoving) {
			if (e.key === 'ArrowLeft' && groupIndex > 0) {
				e.preventDefault();
				const targetGroup = sortedGroups[groupIndex - 1];
				onMoveTask?.(selectedTaskId, targetGroup.id);
				announcer.announce(`${targetGroup.name} 컬럼으로 이동`);
			} else if (e.key === 'ArrowRight' && groupIndex < sortedGroups.length - 1) {
				e.preventDefault();
				const targetGroup = sortedGroups[groupIndex + 1];
				onMoveTask?.(selectedTaskId, targetGroup.id);
				announcer.announce(`${targetGroup.name} 컬럼으로 이동`);
			} else if (e.key === 'ArrowUp' && taskIndex > 0) {
				e.preventDefault();
				const taskIds = sortedTasks.map((t) => t.id);
				const temp = taskIds[taskIndex];
				taskIds[taskIndex] = taskIds[taskIndex - 1];
				taskIds[taskIndex - 1] = temp;
				onReorderTasks?.(group.id, taskIds);
				announcer.announce(`위로 이동, ${taskIndex}번째 위치`);
			} else if (e.key === 'ArrowDown' && taskIndex < sortedTasks.length - 1) {
				e.preventDefault();
				const taskIds = sortedTasks.map((t) => t.id);
				const temp = taskIds[taskIndex];
				taskIds[taskIndex] = taskIds[taskIndex + 1];
				taskIds[taskIndex + 1] = temp;
				onReorderTasks?.(group.id, taskIds);
				announcer.announce(`아래로 이동, ${taskIndex + 2}번째 위치`);
			}
		} else {
			if (e.key === 'ArrowUp' && taskIndex > 0) {
				e.preventDefault();
				selectedTaskId = sortedTasks[taskIndex - 1].id;
			} else if (e.key === 'ArrowDown' && taskIndex < sortedTasks.length - 1) {
				e.preventDefault();
				selectedTaskId = sortedTasks[taskIndex + 1].id;
			} else if (e.key === 'ArrowLeft' && groupIndex > 0) {
				e.preventDefault();
				const prevGroup = sortedGroups[groupIndex - 1];
				const prevTasks = [...prevGroup.tasks].sort((a, b) => a.position - b.position);
				if (prevTasks.length > 0) {
					selectedTaskId = prevTasks[Math.min(taskIndex, prevTasks.length - 1)].id;
				}
			} else if (e.key === 'ArrowRight' && groupIndex < sortedGroups.length - 1) {
				e.preventDefault();
				const nextGroup = sortedGroups[groupIndex + 1];
				const nextTasks = [...nextGroup.tasks].sort((a, b) => a.position - b.position);
				if (nextTasks.length > 0) {
					selectedTaskId = nextTasks[Math.min(taskIndex, nextTasks.length - 1)].id;
				}
			}
		}
	}

	// ── 태스크 D&D ──

	function handleTaskDragStart(e: DragEvent, task: Task) {
		draggedTask = task;
		dragSourceGroupId = task.taskGroup?.id || board.taskGroups.find((g) => g.tasks.some((t) => t.id === task.id))?.id || null;
		e.dataTransfer?.setData('text/plain', task.id);
		e.dataTransfer!.effectAllowed = 'move';
	}

	function handleDragOver(e: DragEvent, targetGroup: TaskGroup) {
		if (!draggedTask) return;
		e.preventDefault();
		dropTargetGroupId = targetGroup.id;

		// 컬럼 내 모든 listitem의 Y좌표를 순회하여 삽입 위치 계산
		// (e.target 기반 closest는 카드 간 gap에서 실패하므로 사용하지 않음)
		const columnEl = (e.target as HTMLElement).closest('[role="list"]') as HTMLElement | null;
		if (!columnEl) { dropIndex = 0; return; }

		const listItems = columnEl.querySelectorAll<HTMLElement>('[role="listitem"]');
		if (listItems.length === 0) { dropIndex = 0; return; }

		let newIndex = listItems.length;
		for (let i = 0; i < listItems.length; i++) {
			const rect = listItems[i].getBoundingClientRect();
			const midY = rect.top + rect.height / 2;
			if (e.clientY < midY) {
				newIndex = i;
				break;
			}
		}
		dropIndex = newIndex;
	}

	function handleDrop(e: DragEvent, targetGroup: TaskGroup) {
		e.preventDefault();
		if (!draggedTask) return;

		const targetGroupId = targetGroup.id;
		const currentDropIndex = dropIndex;

		if (dragSourceGroupId === targetGroupId) {
			// 같은 컬럼 내 재정렬
			const taskIds = [...targetGroup.tasks]
				.sort((a, b) => a.position - b.position)
				.map((t) => t.id);
			const fromIndex = taskIds.indexOf(draggedTask.id);
			if (fromIndex !== -1 && currentDropIndex !== null) {
				taskIds.splice(fromIndex, 1);
				// fromIndex 제거 후 삽입 인덱스 조정
				const adjustedIndex = currentDropIndex > fromIndex ? currentDropIndex - 1 : currentDropIndex;
				taskIds.splice(adjustedIndex, 0, draggedTask.id);
				onReorderTasks?.(targetGroupId, taskIds);
			}
		} else {
			// 크로스 컬럼 이동 (position 포함)
			onMoveTask?.(draggedTask.id, targetGroupId, currentDropIndex ?? undefined);
		}

		resetTaskDragState();
	}

	function handleDragEnd() {
		resetTaskDragState();
	}

	function resetTaskDragState() {
		draggedTask = null;
		dragSourceGroupId = null;
		dropTargetGroupId = null;
		dropIndex = null;
	}

	function handleTaskSelect(taskId: string) {
		selectedTaskId = taskId;
	}

	// ── 컬럼 D&D (ADMIN 전용) ──

	function handleColumnDragStart(e: DragEvent, groupId: string) {
		draggedGroupId = groupId;
		e.dataTransfer?.setData('text/plain', groupId);
		e.dataTransfer!.effectAllowed = 'move';
	}

	function handleColumnDragOver(e: DragEvent, groupIndex: number) {
		if (!draggedGroupId) return;
		e.preventDefault();
		const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
		const midX = rect.left + rect.width / 2;
		columnDropIndex = e.clientX < midX ? groupIndex : groupIndex + 1;
	}

	function handleColumnDrop(e: DragEvent) {
		e.preventDefault();
		if (!draggedGroupId || columnDropIndex === null) return;

		const ids = sortedGroups.map((g) => g.id);
		const fromIdx = ids.indexOf(draggedGroupId);
		if (fromIdx !== -1) {
			ids.splice(fromIdx, 1);
			const adjustedIndex = columnDropIndex > fromIdx ? columnDropIndex - 1 : columnDropIndex;
			ids.splice(adjustedIndex, 0, draggedGroupId);
			onReorderTaskGroups?.(ids);
		}

		resetColumnDragState();
	}

	function handleColumnDragEnd() {
		resetColumnDragState();
	}

	function resetColumnDragState() {
		draggedGroupId = null;
		columnDropIndex = null;
	}

	// 컬럼별 드롭 인디케이터 계산
	function getColumnDropIndicator(groupIndex: number): 'left' | 'right' | null {
		if (!draggedGroupId || columnDropIndex === null) return null;
		if (columnDropIndex === groupIndex) return 'left';
		if (columnDropIndex === groupIndex + 1) return 'right';
		return null;
	}
</script>

<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<div
	class="flex gap-3 overflow-x-auto scrollbar-hide pb-4"
	role="region"
	aria-label="칸반 보드"
	onkeydown={handleKeyboardNavigation}
	ondragend={draggedTask ? handleDragEnd : handleColumnDragEnd}
>
	{#each sortedGroups as group, groupIndex (group.id)}
		<TaskGroupColumn
			taskGroup={group}
			{isAdmin}
			{onTaskClick}
			{onAddTask}
			onEditName={onEditColumnName}
			onDeleteGroup={onDeleteColumn}
			ondragover={(e) => {
				handleDragOver(e, group);
				if (draggedGroupId) handleColumnDragOver(e, groupIndex);
			}}
			ondrop={(e) => {
				if (draggedGroupId) handleColumnDrop(e);
				else handleDrop(e, group);
			}}
			onTaskDragStart={handleTaskDragStart}
			{selectedTaskId}
			{isMoving}
			onTaskSelect={handleTaskSelect}
			dropIndex={dropTargetGroupId === group.id ? dropIndex : null}
			isDropTarget={dropTargetGroupId === group.id}
			isDraggingTask={draggedTask !== null}
			draggedTaskId={draggedTask?.id ?? null}
			columnDraggable={isAdmin}
			onColumnDragStart={(e) => handleColumnDragStart(e, group.id)}
			isDraggingColumn={draggedGroupId === group.id}
			columnDropIndicator={getColumnDropIndicator(groupIndex)}
		/>
	{/each}

	{#if isAdmin}
		<div class="flex w-72 shrink-0 items-start">
			<button
				class="flex w-full items-center gap-2 rounded-xl border-2 border-dashed border-surface-200 p-4 text-sm text-surface-400 transition-all duration-150 ease-snappy hover:border-surface-300 hover:bg-surface-50 hover:text-surface-500"
				onclick={onAddColumn}
			>
				<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
				</svg>
				컬럼 추가
			</button>
		</div>
	{/if}
</div>
