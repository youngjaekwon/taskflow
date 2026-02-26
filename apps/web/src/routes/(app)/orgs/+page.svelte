<script lang="ts">
	import type { PageProps } from './$types';
	import Button from '$lib/components/ui/Button.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Avatar from '$lib/components/ui/Avatar.svelte';
	import EmptyState from '$lib/components/ui/EmptyState.svelte';
	import Pagination from '$lib/components/ui/Pagination.svelte';

	let { data }: PageProps = $props();

	const ITEMS_PER_PAGE = 9;
	let offset = $state(0);

	let paginatedOrgs = $derived(
		data.organizations.slice(offset, offset + ITEMS_PER_PAGE)
	);

	function getUserRole(org: (typeof data.organizations)[0]) {
		const membership = org.members.find((m) => m.user.id === data.user.id);
		return membership?.role;
	}
</script>

<svelte:head>
	<title>내 조직 - TaskFlow</title>
</svelte:head>

<div class="space-y-4">
	<div class="border-b border-surface-200/60 bg-white px-6 pt-4 pb-4">
		<div class="flex items-center justify-between">
			<div>
				<h1 class="text-lg font-semibold tracking-tight text-surface-900">내 조직</h1>
				<p class="mt-1 text-sm text-surface-500">소속된 조직 목록입니다.</p>
			</div>
			<a href="/orgs/new">
				<Button>새 조직</Button>
			</a>
		</div>
	</div>

	<div class="px-6 pb-6">
	{#if data.organizations.length === 0}
		<EmptyState
			title="소속된 조직이 없습니다"
			description="첫 조직을 만들어 팀 협업을 시작하세요."
		>
			{#snippet icon()}
				<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
				</svg>
			{/snippet}
			{#snippet action()}
				<a href="/orgs/new">
					<Button size="sm">새 조직</Button>
				</a>
			{/snippet}
		</EmptyState>
	{:else}
		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
			{#each paginatedOrgs as org}
				{@const role = getUserRole(org)}
				<a
					href="/orgs/{org.id}"
					class="group block rounded-xl border border-surface-200/60 bg-white p-6 shadow-card transition-all duration-200 ease-smooth hover:shadow-card-hover hover:border-surface-300"
				>
					<div class="flex items-start justify-between">
						<h2 class="text-base font-semibold text-surface-900 transition-colors group-hover:text-brand-600">{org.name}</h2>
						{#if role}
							<Badge
								variant={role === 'OWNER' ? 'danger' : role === 'ADMIN' ? 'warning' : 'default'}
								dot
							>
								{role === 'OWNER' ? '소유자' : role === 'ADMIN' ? '관리자' : '멤버'}
							</Badge>
						{/if}
					</div>
					{#if org.description}
						<p class="mt-2 text-sm text-surface-500 line-clamp-2">{org.description}</p>
					{/if}
					<div class="mt-4 flex items-center gap-2">
						<div class="flex -space-x-1.5">
							{#each org.members.slice(0, 3) as member}
								<Avatar
									src={member.user.profileImage}
									alt="{member.user.firstName} {member.user.lastName}"
									size="sm"
								/>
							{/each}
						</div>
						<span class="text-xs text-surface-400">{org.members.length}명의 멤버</span>
					</div>
				</a>
			{/each}
		</div>
		<div class="mt-6">
			<Pagination
				totalCount={data.organizations.length}
				limit={ITEMS_PER_PAGE}
				{offset}
				onPageChange={(newOffset) => (offset = newOffset)}
			/>
		</div>
	{/if}
	</div>
</div>
