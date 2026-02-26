<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { LayoutProps } from './$types';
	import { page } from '$app/state';
	import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';

	let { data, children }: LayoutProps & { children: Snippet } = $props();

	let currentPath = $derived(page.url.pathname);
	let basePath = $derived(`/orgs/${data.org.id}/projects/${data.project.id}`);
	let boardsBasePath = $derived(`${basePath}/boards`);
	let settingsHref = $derived(`${basePath}/settings`);

	let isBoardPage = $derived(currentPath.startsWith(boardsBasePath));
	let isSettingsActive = $derived(currentPath.startsWith(settingsHref));

	function isBoardActive(boardHref: string) {
		return currentPath === boardHref;
	}
</script>

<div class="space-y-4">
	<!-- 브레드크럼 + 프로젝트 내비게이션 탭 -->
	<div class="border-b border-surface-200/60 bg-white px-6 pt-4">
		<Breadcrumb items={[
			{ label: '내 조직', href: '/orgs' },
			{ label: data.org.name, href: `/orgs/${data.org.id}` },
			{ label: data.project.name }
		]} />
		<div class="flex items-center gap-6">
			<h1 class="text-lg font-semibold tracking-tight text-surface-900">{data.project.name}</h1>
		</div>
		<nav class="mt-4 flex gap-1">
			{#each data.boards as board}
				{@const boardHref = `${boardsBasePath}/${board.id}`}
				<a
					href={boardHref}
					class="relative px-3 pb-3 text-sm transition-colors {isBoardActive(boardHref)
						? 'font-medium text-brand-600'
						: 'text-surface-500 hover:text-surface-700'}"
				>
					{board.name}
					{#if isBoardActive(boardHref)}
						<span class="absolute bottom-0 left-0 right-0 h-0.5 rounded-full bg-brand-600"></span>
					{/if}
				</a>
			{/each}
			<a
				href={settingsHref}
				class="relative px-3 pb-3 text-sm transition-colors {isSettingsActive
					? 'font-medium text-brand-600'
					: 'text-surface-500 hover:text-surface-700'}"
			>
				설정
				{#if isSettingsActive}
					<span class="absolute bottom-0 left-0 right-0 h-0.5 rounded-full bg-brand-600"></span>
				{/if}
			</a>
		</nav>
	</div>

	<div class="px-6 pb-6">
		{@render children()}
	</div>
</div>
