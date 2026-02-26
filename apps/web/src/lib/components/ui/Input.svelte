<script lang="ts">
	import type { HTMLInputAttributes } from 'svelte/elements';

	interface Props extends HTMLInputAttributes {
		label?: string;
		error?: string;
		hint?: string;
		validate?: (value: string) => string | null;
		validateOn?: 'blur' | 'input';
	}

	let { label, error, hint, validate, validateOn = 'blur', id, class: className = '', ...rest }: Props = $props();

	let clientError = $state<string | null>(null);
	let touched = $state(false);

	let displayError = $derived(error || (touched ? clientError : null));

	function handleValidation(e: Event) {
		if (!validate) return;
		const value = (e.target as HTMLInputElement).value;
		clientError = validate(value);
	}

	function handleBlur(e: Event) {
		touched = true;
		if (validateOn === 'blur') handleValidation(e);
	}

	function handleInput(e: Event) {
		if (touched && validateOn === 'input') handleValidation(e);
	}
</script>

<div class="flex flex-col gap-1.5">
	{#if label}
		<label for={id} class="text-sm font-medium text-surface-700">{label}</label>
	{/if}
	<input
		{id}
		class="block h-9 w-full rounded-lg border bg-white px-3 text-sm transition-all duration-150 ease-snappy placeholder:text-surface-400 hover:border-surface-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500/20 focus-visible:border-brand-500 {displayError
			? 'border-danger-500 focus-visible:ring-danger-500/20 focus-visible:border-danger-500'
			: 'border-surface-200'} {className}"
		onblur={handleBlur}
		oninput={handleInput}
		{...rest}
	/>
	{#if displayError}
		<p class="flex items-center gap-1 text-sm text-danger-600">
			<svg class="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			{displayError}
		</p>
	{:else if hint}
		<p class="text-sm text-surface-500">{hint}</p>
	{/if}
</div>
