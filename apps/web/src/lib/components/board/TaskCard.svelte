<script lang="ts">
	import type { Task } from '$lib/types';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Avatar from '$lib/components/ui/Avatar.svelte';

	interface Props {
		task: Task;
		onclick?: () => void;
		draggable?: boolean;
		ondragstart?: (e: DragEvent) => void;
		selected?: boolean;
		moving?: boolean;
		isDragging?: boolean;
		onfocus?: () => void;
	}

	let { task, onclick, draggable = false, ondragstart, selected = false, moving = false, isDragging = false, onfocus }: Props = $props();

	// task.status와 task.priority는 서버에서 대문자/소문자 혼용 가능하므로 lowercase 변환
	let status = $derived(task.status.toLowerCase());
	let priority = $derived(task.priority.toLowerCase());

	const statusColors: Record<string, 'default' | 'info' | 'warning' | 'success'> = {
		todo: 'default',
		in_progress: 'info',
		in_review: 'warning',
		done: 'success'
	};

	const statusLabels: Record<string, string> = {
		todo: 'To Do',
		in_progress: 'In Progress',
		in_review: 'In Review',
		done: 'Done'
	};

	const priorityColors: Record<string, string> = {
		low: 'bg-surface-400',
		medium: 'bg-brand-400',
		high: 'bg-warning-500',
		urgent: 'bg-danger-500'
	};

	const priorityBorders: Record<string, string> = {
		low: '',
		medium: 'border-l-3 border-l-brand-400',
		high: 'border-l-3 border-l-warning-500',
		urgent: 'border-l-3 border-l-danger-500'
	};

	const priorityLabels: Record<string, string> = {
		low: 'Low',
		medium: 'Medium',
		high: 'High',
		urgent: 'Urgent'
	};
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_no_noninteractive_tabindex -->
<div
	class="group cursor-pointer rounded-lg border bg-white p-3 shadow-card transition-all duration-200 ease-smooth hover:shadow-card-hover hover:border-surface-300 {priorityBorders[priority]} {selected ? 'ring-2 ring-brand-500 border-brand-300' : 'border-surface-200/60'} {moving ? 'ring-2 ring-brand-500 bg-brand-50/50' : ''} {isDragging ? 'opacity-40 ring-2 ring-brand-300 ring-dashed' : ''}"
	{draggable}
	{ondragstart}
	onclick={onclick}
	{onfocus}
	onkeydown={(e) => e.key === 'Enter' && onclick?.()}
	role={onclick ? 'button' : undefined}
	tabindex={onclick ? 0 : undefined}
	aria-selected={selected}
>
	<div class="flex items-start justify-between gap-2">
		<h3 class="text-sm font-medium leading-snug text-surface-900">{task.title}</h3>
		<span class="flex items-center gap-1" title={priorityLabels[priority]}>
			{#if priority === 'urgent'}
				<svg class="h-3.5 w-3.5 text-danger-500 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
			{:else if priority === 'high'}
				<svg class="h-3.5 w-3.5 text-warning-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
				</svg>
			{:else}
				<span class="h-2 w-2 shrink-0 rounded-full {priorityColors[priority]}"></span>
			{/if}
		</span>
	</div>

	<div class="mt-2 flex flex-wrap items-center gap-1.5">
		<Badge variant={statusColors[status]} dot>{statusLabels[status]}</Badge>
		{#each task.labels as label}
			<span
				class="inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium text-white"
				style="background-color: {label.color}"
			>
				{label.name}
			</span>
		{/each}
	</div>

	<div class="mt-2.5 flex items-center justify-between">
		<div class="flex items-center gap-3 text-xs text-surface-400">
			{#if task.dueDate}
				<span class="flex items-center gap-1">
					<svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
					</svg>
					{new Date(task.dueDate).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
				</span>
			{/if}
			{#if task.commentCount > 0}
				<span class="flex items-center gap-1">
					<svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
					</svg>
					{task.commentCount}
				</span>
			{/if}
		</div>
		{#if task.assignee}
			<Avatar
				src={task.assignee.profileImage}
				alt="{task.assignee.firstName} {task.assignee.lastName}"
				size="sm"
			/>
		{/if}
	</div>
</div>
