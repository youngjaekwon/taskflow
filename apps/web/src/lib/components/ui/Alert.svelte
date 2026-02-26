<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		variant?: 'success' | 'error' | 'warning' | 'info';
		children: Snippet;
	}

	let { variant = 'info', children }: Props = $props();

	const styles = {
		success: {
			container: 'bg-success-50 border-success-100 text-success-700',
			icon: 'text-success-500'
		},
		error: {
			container: 'bg-danger-50 border-danger-100 text-danger-700',
			icon: 'text-danger-500'
		},
		warning: {
			container: 'bg-warning-50 border-warning-100 text-warning-700',
			icon: 'text-warning-500'
		},
		info: {
			container: 'bg-info-50 border-info-100 text-info-700',
			icon: 'text-info-500'
		}
	};

	const icons = {
		success:
			'M5 13l4 4L19 7',
		error:
			'M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
		warning:
			'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z',
		info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
	};
</script>

<div class="flex items-start gap-3 rounded-lg border p-4 text-sm {styles[variant].container}">
	<svg class="mt-0.5 h-4 w-4 shrink-0 {styles[variant].icon}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
		<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={icons[variant]} />
	</svg>
	<div>{@render children()}</div>
</div>
