<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		icon?: Snippet;
		title: string;
		description?: string;
		action?: Snippet;
	}

	let { icon, title, description, action }: Props = $props();
</script>

<div class="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-surface-200 px-6 py-16 text-center animate-fade-in">
	{#if icon}
		<div class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-surface-100 text-surface-400 empty-state-float">
			{@render icon()}
		</div>
	{/if}
	<h3 class="text-sm font-semibold text-surface-900">{title}</h3>
	{#if description}
		<p class="mt-1 text-sm text-surface-500">{description}</p>
	{/if}
	{#if action}
		<div class="mt-4">
			{@render action()}
		</div>
	{/if}
</div>

<style>
	.empty-state-float {
		animation: float 3s ease-in-out infinite;
	}

	@keyframes float {
		0%, 100% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(-6px);
		}
	}
</style>
