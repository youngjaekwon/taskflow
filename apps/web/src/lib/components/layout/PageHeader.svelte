<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		title: string;
		description?: string;
		actions?: Snippet;
	}

	let { title, description, actions }: Props = $props();
</script>

<div class="mb-8 flex items-center justify-between">
	<div>
		<h1 class="text-xl font-semibold tracking-tight text-surface-900">{title}</h1>
		{#if description}
			<p class="mt-1 text-sm text-surface-500">{description}</p>
		{/if}
	</div>
	{#if actions}
		<div class="flex items-center gap-2">
			{@render actions()}
		</div>
	{/if}
</div>
