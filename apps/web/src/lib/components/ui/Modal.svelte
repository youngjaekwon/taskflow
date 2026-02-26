<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		open: boolean;
		onclose: () => void;
		title?: string;
		description?: string;
		size?: 'sm' | 'md' | 'lg';
		children: Snippet;
		footer?: Snippet;
	}

	let { open, onclose, title, description, size = 'md', children, footer }: Props = $props();

	const sizes = {
		sm: 'max-w-sm',
		md: 'max-w-lg',
		lg: 'max-w-2xl'
	};

	let panelEl = $state<HTMLDivElement>();
	let previousActiveElement: Element | null = null;

	const FOCUSABLE_SELECTOR = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

	$effect(() => {
		if (open) {
			previousActiveElement = document.activeElement;
			// 다음 틱에서 첫 focusable 요소에 포커스
			requestAnimationFrame(() => {
				if (panelEl) {
					const first = panelEl.querySelector<HTMLElement>(FOCUSABLE_SELECTOR);
					first?.focus();
				}
			});
		} else if (previousActiveElement) {
			(previousActiveElement as HTMLElement).focus?.();
			previousActiveElement = null;
		}
	});

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) onclose();
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			onclose();
			return;
		}

		if (e.key === 'Tab' && panelEl) {
			const focusable = Array.from(panelEl.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR));
			if (focusable.length === 0) return;

			const first = focusable[0];
			const last = focusable[focusable.length - 1];

			if (e.shiftKey) {
				if (document.activeElement === first) {
					e.preventDefault();
					last.focus();
				}
			} else {
				if (document.activeElement === last) {
					e.preventDefault();
					first.focus();
				}
			}
		}
	}
</script>

{#if open}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<!-- svelte-ignore a11y_interactive_supports_focus -->
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-fade-in"
		onclick={handleBackdropClick}
		onkeydown={handleKeydown}
		role="dialog"
		aria-modal="true"
		aria-label={title}
	>
		<div class="w-full {sizes[size]} rounded-xl border border-surface-200/60 bg-white shadow-modal animate-scale-in" bind:this={panelEl}>
			{#if title}
				<div class="flex items-center justify-between border-b border-surface-100 px-6 py-4">
					<div>
						<h2 class="text-base font-semibold text-surface-900">{title}</h2>
						{#if description}
							<p class="mt-0.5 text-sm text-surface-500">{description}</p>
						{/if}
					</div>
					<button
						class="flex h-8 w-8 items-center justify-center rounded-lg text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-600"
						onclick={onclose}
						aria-label="닫기"
					>
						<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				</div>
			{/if}
			<div class="px-6 py-4">
				{@render children()}
			</div>
			{#if footer}
				<div class="flex justify-end gap-2 border-t border-surface-100 px-6 py-4">
					{@render footer()}
				</div>
			{/if}
		</div>
	</div>
{/if}
