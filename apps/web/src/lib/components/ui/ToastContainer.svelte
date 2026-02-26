<script lang="ts">
	import { toastStore } from '$lib/stores/toast.svelte';
	import Toast from './Toast.svelte';
</script>

{#if toastStore.toasts.length > 0}
	<div class="pointer-events-none fixed bottom-4 right-4 z-50 flex flex-col gap-2">
		{#each toastStore.toasts as toast (toast.id)}
			<Toast
				id={toast.id}
				message={toast.message}
				variant={toast.variant}
				duration={toast.duration}
				onclose={(id) => toastStore.remove(id)}
			/>
		{/each}
	</div>
{/if}
