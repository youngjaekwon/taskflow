<script lang="ts">
	import type { PageProps } from './$types';
	import Button from '$lib/components/ui/Button.svelte';
	import Avatar from '$lib/components/ui/Avatar.svelte';
	import EmptyState from '$lib/components/ui/EmptyState.svelte';
	import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title>프로젝트 - {data.org.name} - TaskFlow</title>
</svelte:head>

<div class="space-y-4">
<div class="border-b border-surface-200/60 bg-white px-6 pt-4 pb-4">
	<Breadcrumb items={[
		{ label: '내 조직', href: '/orgs' },
		{ label: data.org.name, href: `/orgs/${data.org.id}` },
		{ label: '프로젝트' }
	]} />
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-lg font-semibold tracking-tight text-surface-900">프로젝트</h1>
			<p class="mt-1 text-sm text-surface-500">{data.org.name}의 프로젝트 목록</p>
		</div>
		{#if data.isAdmin}
			<a href="/orgs/{data.org.id}/projects/new">
				<Button>새 프로젝트</Button>
			</a>
		{/if}
	</div>
</div>

<div class="px-6 pb-6">
{#if data.projects.length === 0}
	<EmptyState
		title="프로젝트가 없습니다"
		description={data.isAdmin ? '첫 프로젝트를 만들어보세요.' : '아직 생성된 프로젝트가 없습니다.'}
	>
		{#snippet icon()}
			<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
			</svg>
		{/snippet}
		{#snippet action()}
			{#if data.isAdmin}
				<a href="/orgs/{data.org.id}/projects/new">
					<Button size="sm">새 프로젝트</Button>
				</a>
			{/if}
		{/snippet}
	</EmptyState>
{:else}
	<div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
		{#each data.projects as project}
			<a
				href="/orgs/{data.org.id}/projects/{project.id}"
				class="group block rounded-xl border border-surface-200/60 bg-white p-6 shadow-card transition-all duration-200 ease-smooth hover:shadow-card-hover hover:border-surface-300"
			>
				<h2 class="text-base font-semibold text-surface-900 transition-colors group-hover:text-brand-600">{project.name}</h2>
				{#if project.description}
					<p class="mt-2 text-sm text-surface-500 line-clamp-2">{project.description}</p>
				{/if}
				<div class="mt-4 flex items-center gap-2">
					<div class="flex -space-x-1.5">
						{#each project.members.slice(0, 3) as member}
							<Avatar
								src={member.user.profileImage}
								alt="{member.user.firstName} {member.user.lastName}"
								size="sm"
							/>
						{/each}
					</div>
					<span class="text-xs text-surface-400">{project.members.length}명의 멤버</span>
				</div>
			</a>
		{/each}
	</div>
{/if}
</div>
</div>
