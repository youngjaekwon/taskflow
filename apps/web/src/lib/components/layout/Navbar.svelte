<script lang="ts">
	import { enhance } from '$app/forms';
	import Avatar from '$lib/components/ui/Avatar.svelte';
	import DropdownMenu from '$lib/components/ui/DropdownMenu.svelte';
	import { sidebarStore } from '$lib/stores/sidebar.svelte';

	interface Props {
		user: {
			firstName: string;
			lastName: string;
			email: string;
			profileImage: string | null;
		} | null;
	}

	let { user }: Props = $props();
</script>

<header class="sticky top-0 z-30 border-b border-surface-200/60 bg-white/80 backdrop-blur-md">
	<div class="flex h-14 items-center justify-between px-4 sm:px-6">
		<div class="flex items-center gap-2">
			<!-- 모바일 햄버거 버튼 -->
			{#if user}
				<button
					class="rounded-lg p-1.5 text-surface-500 transition-colors hover:bg-surface-100 hover:text-surface-700 lg:hidden"
					onclick={() => sidebarStore.toggle()}
					aria-label="메뉴 열기"
				>
					<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
					</svg>
				</button>
			{/if}
			<a href="/" class="flex items-center gap-2 text-lg font-bold text-surface-900">
				<svg class="h-6 w-6 text-brand-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
				</svg>
				TaskFlow
			</a>
		</div>

		<nav class="flex items-center gap-1">
			{#if user}
				<DropdownMenu align="right">
					{#snippet trigger()}
						<Avatar
							src={user.profileImage}
							alt="{user.firstName} {user.lastName}"
							size="sm"
						/>
					{/snippet}
					{#snippet children()}
						{#if user.firstName || user.lastName || user.email}
						<div class="px-4 py-2">
							{#if user.firstName || user.lastName}
								<p class="text-sm font-medium text-surface-900">{[user.firstName, user.lastName].filter(Boolean).join(' ')}</p>
							{/if}
							{#if user.email}
								<p class="text-xs text-surface-500">{user.email}</p>
							{/if}
						</div>
						<hr class="border-surface-100" />
					{/if}
						<a
							href="/orgs"
							class="block px-4 py-2 text-sm text-surface-700 transition-colors hover:bg-surface-50"
							role="menuitem"
						>
							내 조직
						</a>
						<a
							href="/profile"
							class="block px-4 py-2 text-sm text-surface-700 transition-colors hover:bg-surface-50"
							role="menuitem"
						>
							프로필
						</a>
						<hr class="border-surface-100" />
						<form method="POST" action="/logout" use:enhance>
							<button
								type="submit"
								class="block w-full px-4 py-2 text-left text-sm text-danger-600 transition-colors hover:bg-surface-50"
								role="menuitem"
							>
								로그아웃
							</button>
						</form>
					{/snippet}
				</DropdownMenu>
			{:else}
				<a
					href="/login"
					class="rounded-lg px-3 py-1.5 text-sm text-surface-600 transition-colors hover:bg-surface-100 hover:text-surface-900"
				>
					로그인
				</a>
				<a
					href="/register"
					class="rounded-lg bg-brand-600 px-4 py-1.5 text-sm font-medium text-white transition-colors hover:bg-brand-700"
				>
					회원가입
				</a>
			{/if}
		</nav>
	</div>
</header>
