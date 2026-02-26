<script lang="ts">
	import Skeleton from '../Skeleton.svelte';
</script>

<div class="mb-4">
	<Skeleton width="12rem" height="1.5rem" />
</div>
<div class="flex gap-3 overflow-hidden">
	{#each { length: 3 } as _}
		<div class="w-72 shrink-0 rounded-xl bg-surface-100/50 p-3">
			<div class="flex items-center gap-2 mb-3">
				<Skeleton class="!rounded-full" width="0.5rem" height="0.5rem" />
				<Skeleton width="5rem" height="0.75rem" />
				<Skeleton class="!rounded-md" width="1.25rem" height="1.25rem" />
			</div>
			<div class="space-y-2">
				{#each { length: 3 } as __}
					<div class="rounded-lg border border-surface-200/60 bg-white p-3">
						<Skeleton width="80%" height="0.875rem" />
						<div class="mt-2 flex gap-1.5">
							<Skeleton class="!rounded-md" width="3.5rem" height="1.25rem" />
						</div>
						<div class="mt-2.5 flex items-center justify-between">
							<Skeleton width="3rem" height="0.75rem" />
							<Skeleton class="!rounded-full" width="1.5rem" height="1.5rem" />
						</div>
					</div>
				{/each}
			</div>
		</div>
	{/each}
</div>
