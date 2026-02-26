<script lang="ts">
	interface BreadcrumbItem {
		label: string;
		href?: string;
	}

	interface Props {
		items: BreadcrumbItem[];
	}

	let { items }: Props = $props();
</script>

<nav aria-label="경로" class="mb-4">
	<ol class="flex items-center gap-1 text-sm">
		{#each items as item, i}
			{#if i > 0}
				<li aria-hidden="true" class="text-surface-300">
					<svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
					</svg>
				</li>
			{/if}
			<li class={i < items.length - 2 ? 'hidden sm:block' : ''}>
				{#if i === items.length - 1}
					<span class="font-medium text-surface-900" aria-current="page">{item.label}</span>
				{:else if item.href}
					<a href={item.href} class="text-surface-500 transition-colors hover:text-brand-600">{item.label}</a>
				{:else}
					<span class="text-surface-500">{item.label}</span>
				{/if}
			</li>
		{/each}
	</ol>
</nav>
