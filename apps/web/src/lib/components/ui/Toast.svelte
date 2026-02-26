<script lang="ts">
	import type { ToastVariant } from '$lib/stores/toast.svelte';

	interface Props {
		id: string;
		message: string;
		variant: ToastVariant;
		duration: number;
		onclose: (id: string) => void;
	}

	let { id, message, variant, duration, onclose }: Props = $props();

	const styles: Record<ToastVariant, { container: string; icon: string; progress: string }> = {
		success: {
			container: 'bg-white border-success-200 text-surface-900',
			icon: 'text-success-500',
			progress: 'bg-success-500'
		},
		error: {
			container: 'bg-white border-danger-200 text-surface-900',
			icon: 'text-danger-500',
			progress: 'bg-danger-500'
		},
		warning: {
			container: 'bg-white border-warning-200 text-surface-900',
			icon: 'text-warning-500',
			progress: 'bg-warning-500'
		},
		info: {
			container: 'bg-white border-info-200 text-surface-900',
			icon: 'text-info-500',
			progress: 'bg-info-500'
		}
	};

	const icons: Record<ToastVariant, string> = {
		success: 'M5 13l4 4L19 7',
		error: 'M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
		warning:
			'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z',
		info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
	};
</script>

<div
	class="pointer-events-auto flex w-80 items-start gap-3 overflow-hidden rounded-lg border p-4 shadow-dropdown animate-slide-up {styles[variant].container}"
	role="status"
	aria-live="polite"
>
	<svg
		class="mt-0.5 h-4 w-4 shrink-0 {styles[variant].icon}"
		fill="none"
		viewBox="0 0 24 24"
		stroke="currentColor"
	>
		<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={icons[variant]} />
	</svg>
	<p class="flex-1 text-sm">{message}</p>
	<button
		class="shrink-0 rounded-md p-0.5 text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-600"
		onclick={() => onclose(id)}
		aria-label="닫기"
	>
		<svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M6 18L18 6M6 6l12 12"
			/>
		</svg>
	</button>
	<!-- 프로그레스 바 -->
	<div class="absolute bottom-0 left-0 right-0 h-0.5 bg-surface-100">
		<div
			class="h-full {styles[variant].progress}"
			style="animation: toast-progress {duration}ms linear forwards"
		></div>
	</div>
</div>

<style>
	@keyframes toast-progress {
		from {
			width: 100%;
		}
		to {
			width: 0%;
		}
	}
</style>
