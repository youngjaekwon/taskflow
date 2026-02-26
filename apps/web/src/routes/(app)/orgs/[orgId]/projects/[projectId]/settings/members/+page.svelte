<script lang="ts">
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';
	import Button from '$lib/components/ui/Button.svelte';
	import Avatar from '$lib/components/ui/Avatar.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import PageHeader from '$lib/components/layout/PageHeader.svelte';

	let { data, form }: PageProps = $props();

	let availableMembers = $derived(
		data.org.members.filter(
			(orgMember) =>
				!data.project.members.some((pm) => pm.user.id === orgMember.user.id)
		)
	);
</script>

<svelte:head>
	<title>멤버 - {data.project.name} - TaskFlow</title>
</svelte:head>

<PageHeader title="프로젝트 멤버" description="{data.project.members.length}명의 멤버" />

{#if form?.success}
	<div class="mb-6"><Alert variant="success">완료되었습니다.</Alert></div>
{/if}
{#if form?.error}
	<div class="mb-6"><Alert variant="error">{form.error}</Alert></div>
{/if}

{#if data.isAdmin}
	<section class="mb-6 rounded-xl border border-surface-200/60 bg-white p-6 shadow-card">
		<h2 class="mb-4 text-sm font-semibold text-surface-900">멤버 추가</h2>
		{#if availableMembers.length > 0}
			<form method="POST" action="?/add" use:enhance class="flex gap-2">
				<select
					name="user_id"
					class="h-9 flex-1 rounded-lg border border-surface-200 bg-white px-3 text-sm transition-colors hover:border-surface-300"
					required
				>
					<option value="">조직 멤버 선택</option>
					{#each availableMembers as member}
						<option value={member.user.id}>
							{member.user.firstName} {member.user.lastName || member.user.username} ({member.user.email})
						</option>
					{/each}
				</select>
				<Button type="submit">추가</Button>
			</form>
		{:else}
			<p class="text-sm text-surface-500">추가할 수 있는 조직 멤버가 없습니다. 먼저 <a href="/orgs/{data.org.id}/settings/members" class="text-brand-600 hover:text-brand-700">조직 멤버 관리</a>에서 멤버를 초대하세요.</p>
		{/if}
	</section>
{/if}

<section class="rounded-xl border border-surface-200/60 bg-white shadow-card">
	<table class="w-full">
		<thead>
			<tr class="border-b border-surface-100 text-left text-sm text-surface-500">
				<th class="px-6 py-3 font-medium">멤버</th>
				<th class="px-6 py-3 font-medium">추가일</th>
				{#if data.isAdmin}
					<th class="px-6 py-3 font-medium">관리</th>
				{/if}
			</tr>
		</thead>
		<tbody>
			{#each data.project.members as member}
				<tr class="border-b border-surface-100 last:border-0">
					<td class="px-6 py-4">
						<div class="flex items-center gap-3">
							<Avatar
								src={member.user.profileImage}
								alt="{member.user.firstName} {member.user.lastName}"
								size="sm"
							/>
							<div>
								<p class="text-sm font-medium text-surface-900">
									{member.user.firstName} {member.user.lastName || member.user.username}
								</p>
								<p class="text-xs text-surface-500">{member.user.email}</p>
							</div>
						</div>
					</td>
					<td class="px-6 py-4 text-sm text-surface-500">
						{new Date(member.joinedAt).toLocaleDateString('ko-KR')}
					</td>
					{#if data.isAdmin}
						<td class="px-6 py-4">
							<form method="POST" action="?/remove" use:enhance>
								<input type="hidden" name="user_id" value={member.user.id} />
								<Button type="submit" variant="ghost" size="sm">제거</Button>
							</form>
						</td>
					{/if}
				</tr>
			{/each}
		</tbody>
	</table>
</section>
