<script lang="ts">
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();
</script>

<main id="main-content" class="flex min-h-[calc(100vh-3.5rem)] items-center justify-center bg-surface-50 px-4">
	<div class="w-full max-w-sm">
		<!-- 로고 -->
		<div class="mb-8 flex justify-center">
			<a href="/" class="flex items-center gap-2 text-lg font-bold text-surface-900">
				<svg class="h-7 w-7 text-brand-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
				</svg>
				TaskFlow
			</a>
		</div>
		<div class="rounded-xl border border-surface-200/60 bg-white p-6 shadow-card">
			{@render children()}
		</div>
	</div>
</main>
