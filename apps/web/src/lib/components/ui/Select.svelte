<script lang="ts">
	import type { HTMLSelectAttributes } from 'svelte/elements';

	interface Props extends HTMLSelectAttributes {
		label?: string;
		error?: string;
		options: Array<{ value: string; label: string }>;
	}

	let { label, error, id, options, value, class: className = '', ...rest }: Props = $props();
</script>

<div class="flex flex-col gap-1.5">
	{#if label}
		<label for={id} class="text-sm font-medium text-surface-700">{label}</label>
	{/if}
	<div class="relative">
		<select
			{id}
			class="block h-9 w-full appearance-none rounded-lg border bg-white px-3 pr-8 text-sm transition-all duration-150 ease-snappy hover:border-surface-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500/20 focus-visible:border-brand-500 {error
				? 'border-danger-500 focus-visible:ring-danger-500/20 focus-visible:border-danger-500'
				: 'border-surface-200'} {className}"
			{...rest}
		>
			{#each options as opt}
				<option value={opt.value} selected={value != null && String(value) === opt.value}>{opt.label}</option>
			{/each}
		</select>
		<svg class="pointer-events-none absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
		</svg>
	</div>
	{#if error}
		<p class="flex items-center gap-1 text-sm text-danger-600">
			<svg class="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			{error}
		</p>
	{/if}
</div>
