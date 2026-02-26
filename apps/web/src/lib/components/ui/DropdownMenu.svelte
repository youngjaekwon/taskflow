<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		trigger: Snippet;
		children: Snippet;
		align?: 'left' | 'right';
	}

	let { trigger, children, align = 'right' }: Props = $props();
	let open = $state(false);
	let containerEl: HTMLDivElement;

	function handleClickOutside(e: MouseEvent) {
		if (containerEl && !containerEl.contains(e.target as Node)) {
			open = false;
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') open = false;
	}
</script>

<svelte:window onclick={handleClickOutside} onkeydown={handleKeydown} />

<div class="relative inline-block" bind:this={containerEl}>
	<button onclick={() => (open = !open)} class="flex items-center">
		{@render trigger()}
	</button>
	{#if open}
		<div
			class="absolute z-40 mt-2 min-w-48 rounded-lg border border-surface-200/60 bg-white py-1 shadow-dropdown animate-scale-in {align === 'right'
				? 'right-0'
				: 'left-0'}"
			role="menu"
		>
			<!-- svelte-ignore a11y_click_events_have_key_events -->
			<!-- svelte-ignore a11y_no_static_element_interactions -->
			<div onclick={() => (open = false)}>
				{@render children()}
			</div>
		</div>
	{/if}
</div>
