<script lang="ts">
	interface Props {
		value?: string;
		placeholder?: string;
		onsearch: (query: string) => void;
		debounce?: number;
	}

	let { value = '', placeholder = '검색...', onsearch, debounce: debounceMs = 300 }: Props = $props();

	let inputValue = $state('');
	let timer: ReturnType<typeof setTimeout> | null = null;

	function handleInput(e: Event) {
		const v = (e.target as HTMLInputElement).value;
		inputValue = v;

		if (timer) clearTimeout(timer);
		timer = setTimeout(() => onsearch(v), debounceMs);
	}

	function handleClear() {
		inputValue = '';
		onsearch('');
	}
</script>

<div class="relative">
	<svg
		class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-surface-400"
		fill="none"
		viewBox="0 0 24 24"
		stroke="currentColor"
	>
		<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
	</svg>
	<input
		type="search"
		value={inputValue}
		{placeholder}
		oninput={handleInput}
		class="block h-9 w-full rounded-lg border border-surface-200 bg-white pl-9 pr-8 text-sm transition-all duration-150 ease-snappy placeholder:text-surface-400 hover:border-surface-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500/20 focus-visible:border-brand-500"
	/>
	{#if inputValue}
		<button
			class="absolute right-2 top-1/2 -translate-y-1/2 rounded-md p-0.5 text-surface-400 transition-colors hover:text-surface-600"
			onclick={handleClear}
			aria-label="검색어 지우기"
		>
			<svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
			</svg>
		</button>
	{/if}
</div>
