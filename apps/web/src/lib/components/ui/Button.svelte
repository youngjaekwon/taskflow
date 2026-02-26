<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLButtonAttributes } from 'svelte/elements';

	interface Props extends HTMLButtonAttributes {
		variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
		size?: 'sm' | 'md' | 'lg';
		loading?: boolean;
		children: Snippet;
	}

	let {
		variant = 'primary',
		size = 'md',
		loading = false,
		children,
		class: className = '',
		disabled,
		...rest
	}: Props = $props();

	const base =
		'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-150 ease-snappy focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98] shadow-xs';

	const variants = {
		primary:
			'bg-brand-600 text-white hover:bg-brand-700 disabled:hover:bg-brand-600',
		secondary:
			'bg-surface-100 text-surface-700 hover:bg-surface-200 border border-surface-200 disabled:hover:bg-surface-100',
		danger:
			'bg-danger-600 text-white hover:bg-danger-700 disabled:hover:bg-danger-600',
		ghost:
			'bg-transparent text-surface-600 hover:bg-surface-100 shadow-none disabled:hover:bg-transparent'
	};

	const sizes = {
		sm: 'h-8 px-3 text-xs gap-1.5',
		md: 'h-9 px-4 text-sm gap-2',
		lg: 'h-11 px-6 text-sm gap-2'
	};
</script>

<button
	class="{base} {variants[variant]} {sizes[size]} {className}"
	disabled={disabled || loading}
	{...rest}
>
	{#if loading}
		<svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
			<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
		</svg>
	{/if}
	{@render children()}
</button>
