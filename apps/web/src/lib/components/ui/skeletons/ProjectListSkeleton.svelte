<script lang="ts">
	import Skeleton from '../Skeleton.svelte';
</script>

<div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
	{#each { length: 3 } as _}
		<div class="rounded-xl border border-surface-200/60 bg-white p-6 shadow-card">
			<Skeleton width="60%" height="1.25rem" />
			<div class="mt-3">
				<Skeleton width="100%" height="0.875rem" />
				<Skeleton class="mt-1" width="75%" height="0.875rem" />
			</div>
			<div class="mt-4 flex items-center gap-2">
				<div class="flex -space-x-1.5">
					{#each { length: 2 } as __}
						<Skeleton class="!rounded-full" width="1.5rem" height="1.5rem" />
					{/each}
				</div>
				<Skeleton width="4rem" height="0.75rem" />
			</div>
		</div>
	{/each}
</div>
