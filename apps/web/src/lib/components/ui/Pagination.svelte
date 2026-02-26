<script lang="ts">
	interface Props {
		totalCount: number;
		limit: number;
		offset: number;
		onPageChange: (offset: number) => void;
	}

	let { totalCount, limit, offset, onPageChange }: Props = $props();

	let currentPage = $derived(Math.floor(offset / limit) + 1);
	let totalPages = $derived(Math.ceil(totalCount / limit));
	let hasPrevious = $derived(offset > 0);
	let hasNext = $derived(offset + limit < totalCount);
</script>

{#if totalPages > 1}
	<nav class="flex items-center justify-between" aria-label="페이지네이션">
		<p class="text-sm text-surface-500">
			총 <span class="font-medium text-surface-700">{totalCount}</span>건 중
			<span class="font-medium text-surface-700">{offset + 1}</span>–<span
				class="font-medium text-surface-700">{Math.min(offset + limit, totalCount)}</span
			>
		</p>
		<div class="flex gap-1">
			<button
				class="inline-flex h-8 items-center rounded-lg border border-surface-200 px-3 text-sm font-medium text-surface-600 transition-all duration-150 ease-snappy hover:bg-surface-100 disabled:opacity-50 disabled:cursor-not-allowed"
				disabled={!hasPrevious}
				onclick={() => onPageChange(offset - limit)}
			>
				이전
			</button>
			<span
				class="inline-flex h-8 items-center rounded-lg bg-brand-50 px-3 text-sm font-medium text-brand-700"
			>
				{currentPage} / {totalPages}
			</span>
			<button
				class="inline-flex h-8 items-center rounded-lg border border-surface-200 px-3 text-sm font-medium text-surface-600 transition-all duration-150 ease-snappy hover:bg-surface-100 disabled:opacity-50 disabled:cursor-not-allowed"
				disabled={!hasNext}
				onclick={() => onPageChange(offset + limit)}
			>
				다음
			</button>
		</div>
	</nav>
{/if}
