<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { LayoutProps } from './$types';
	import { onNavigate } from '$app/navigation';
	import '../app.css';
	import Navbar from '$lib/components/layout/Navbar.svelte';
	import ToastContainer from '$lib/components/ui/ToastContainer.svelte';
	import { announcer } from '$lib/stores/announcer.svelte';

	let { data, children }: LayoutProps & { children: Snippet } = $props();

	onNavigate((navigation) => {
		if (!document.startViewTransition) return;
		return new Promise((resolve) => {
			document.startViewTransition(async () => {
				resolve();
				await navigation.complete;
			});
		});
	});
</script>

<!-- Skip navigation -->
<a
	href="#main-content"
	class="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:rounded-lg focus:bg-brand-600 focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-white focus:shadow-modal"
>
	본문으로 건너뛰기
</a>

<div class="min-h-screen text-surface-900">
	<Navbar user={data.user} />
	{@render children()}
</div>

<ToastContainer />

<!-- ARIA live region for screen reader announcements -->
<div aria-live="polite" aria-atomic="true" class="sr-only">
	{announcer.message}
</div>
