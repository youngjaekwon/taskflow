<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { OrgRole } from '$lib/types';
	import { sidebarStore } from '$lib/stores/sidebar.svelte';

	interface NavItem {
		href: string;
		label: string;
		active?: boolean;
	}

	interface Props {
		title: string;
		items: NavItem[];
		role?: OrgRole;
		children?: Snippet;
	}

	let { title, items, children }: Props = $props();

	function handleLinkClick() {
		// 모바일에서 링크 클릭 시 사이드바 닫기
		sidebarStore.hide();
	}
</script>

<!-- 모바일 오버레이 (sm 이하) -->
{#if sidebarStore.open}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm lg:hidden animate-fade-in"
		onclick={() => sidebarStore.hide()}
		onkeydown={(e) => e.key === 'Escape' && sidebarStore.hide()}
	></div>
{/if}

<!-- 사이드바 -->
<aside
	class="shrink-0 border-r border-surface-200/60 bg-white transition-all duration-200 ease-smooth
		{sidebarStore.open ? 'fixed inset-y-0 left-0 z-50 w-60 pt-14' : 'hidden'}
		lg:relative lg:block lg:w-60 lg:pt-0"
>
	<div class="px-4 pt-5 pb-2">
		<h2 class="truncate text-xs font-semibold uppercase tracking-wider text-surface-400">{title}</h2>
	</div>
	<nav class="space-y-0.5 px-2">
		{#each items as item}
			<a
				href={item.href}
				onclick={handleLinkClick}
				class="block rounded-lg px-3 py-2 text-sm transition-colors {item.active
					? 'bg-brand-50 text-brand-700 font-medium'
					: 'text-surface-600 hover:bg-surface-100 hover:text-surface-900'}"
			>
				{item.label}
			</a>
		{/each}
	</nav>
	{#if children}
		<div class="mt-4 border-t border-surface-200/60 p-4">
			{@render children()}
		</div>
	{/if}
</aside>
