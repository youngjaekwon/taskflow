<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
		dot?: boolean;
		children: Snippet;
		class?: string;
	}

	let { variant = 'default', dot = false, children, class: className = '' }: Props = $props();

	const variants = {
		default: 'bg-surface-100 text-surface-700 border-surface-200',
		success: 'bg-success-50 text-success-700 border-success-100',
		warning: 'bg-warning-50 text-warning-700 border-warning-100',
		danger: 'bg-danger-50 text-danger-700 border-danger-100',
		info: 'bg-info-50 text-info-700 border-info-100'
	};

	const dotColors = {
		default: 'bg-surface-400',
		success: 'bg-success-500',
		warning: 'bg-warning-500',
		danger: 'bg-danger-500',
		info: 'bg-info-500'
	};
</script>

<span
	class="inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-xs font-medium {variants[variant]} {className}"
>
	{#if dot}
		<span class="h-1.5 w-1.5 rounded-full {dotColors[variant]}"></span>
	{/if}
	{@render children()}
</span>
