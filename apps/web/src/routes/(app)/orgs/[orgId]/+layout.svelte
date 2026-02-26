<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { LayoutProps } from './$types';
	import Sidebar from '$lib/components/layout/Sidebar.svelte';
	import { page } from '$app/state';

	let { data, children }: LayoutProps & { children: Snippet } = $props();

	let basePath = $derived(`/orgs/${data.org.id}`);
	let settingsPath = $derived(`/orgs/${data.org.id}/settings`);

	let items = $derived([
		{
			href: basePath,
			label: '프로젝트',
			active: page.url.pathname === basePath || page.url.pathname.startsWith(`${basePath}/projects`)
		},
		{
			href: settingsPath,
			label: '설정',
			active: page.url.pathname.startsWith(settingsPath)
		}
	]);
</script>

<div class="flex min-h-[calc(100vh-3.5rem)]">
	<Sidebar title={data.org.name} {items} />
	<main class="flex-1 overflow-auto">
		{@render children()}
	</main>
</div>
