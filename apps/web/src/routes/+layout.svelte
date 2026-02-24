<script lang="ts">
	import type { Snippet } from 'svelte';
	import '../app.css';

	let { children }: { children: Snippet } = $props();
</script>

<div class="min-h-screen bg-gray-50 text-gray-900">
	{@render children()}
</div>
