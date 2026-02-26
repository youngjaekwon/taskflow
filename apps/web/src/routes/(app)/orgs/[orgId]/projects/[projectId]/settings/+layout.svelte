<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { LayoutProps } from './$types';
	import { page } from '$app/state';

	let { data, children }: LayoutProps & { children: Snippet } = $props();

	let currentPath = $derived(page.url.pathname);
	let basePath = $derived(
		`/orgs/${data.org.id}/projects/${data.project.id}/settings`
	);
	let membersPath = $derived(`${basePath}/members`);

	let tabs = $derived([
		{ href: basePath, label: '기본정보', active: currentPath === basePath },
		{ href: membersPath, label: '멤버', active: currentPath === membersPath }
	]);
</script>

<div class="space-y-4">
	<div class="border-b border-surface-200/60 bg-white px-6 pt-4">
		<div class="flex items-center gap-6">
			<h1 class="text-lg font-semibold tracking-tight text-surface-900">설정</h1>
		</div>
		<nav class="mt-4 flex gap-1">
			{#each tabs as tab}
				<a
					href={tab.href}
					class="relative px-3 pb-3 text-sm transition-colors {tab.active
						? 'font-medium text-brand-600'
						: 'text-surface-500 hover:text-surface-700'}"
				>
					{tab.label}
					{#if tab.active}
						<span class="absolute bottom-0 left-0 right-0 h-0.5 rounded-full bg-brand-600"
						></span>
					{/if}
				</a>
			{/each}
		</nav>
	</div>

	<div class="px-6 pb-6">
		{@render children()}
	</div>
</div>
