<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps & { children: Snippet } = $props();
</script>

<div id="main-content" class="min-h-[calc(100vh-3.5rem)] bg-surface-50">
	{@render children()}
</div>
