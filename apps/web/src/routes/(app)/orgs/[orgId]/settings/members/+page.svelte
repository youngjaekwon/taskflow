<script lang="ts">
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Avatar from '$lib/components/ui/Avatar.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import PageHeader from '$lib/components/layout/PageHeader.svelte';

	let { data, form }: PageProps = $props();

	const roleLabels: Record<string, string> = {
		OWNER: '소유자',
		ADMIN: '관리자',
		MEMBER: '멤버'
	};
</script>

<svelte:head>
	<title>멤버 - {data.org.name} - TaskFlow</title>
</svelte:head>

<PageHeader title="멤버 관리" description="{data.org.members.length}명의 멤버" />

{#if form?.success}
	<div class="mb-6"><Alert variant="success">완료되었습니다.</Alert></div>
{/if}
{#if form?.error}
	<div class="mb-6"><Alert variant="error">{form.error}</Alert></div>
{/if}

{#if data.isAdmin}
	<section class="mb-6 rounded-xl border border-surface-200/60 bg-white p-6 shadow-card">
		<h2 class="mb-4 text-sm font-semibold text-surface-900">멤버 초대</h2>
		<form method="POST" action="?/invite" use:enhance class="flex gap-2">
			<div class="flex-1">
				<Input id="invite-email" name="email" type="email" placeholder="이메일 주소" required />
			</div>
			<Button type="submit">초대</Button>
		</form>
	</section>
{/if}

<section class="rounded-xl border border-surface-200/60 bg-white shadow-card">
	<table class="w-full">
		<thead>
			<tr class="border-b border-surface-100 text-left text-sm text-surface-500">
				<th class="px-6 py-3 font-medium">멤버</th>
				<th class="px-6 py-3 font-medium">역할</th>
				<th class="px-6 py-3 font-medium">가입일</th>
				{#if data.isAdmin}
					<th class="px-6 py-3 font-medium">관리</th>
				{/if}
			</tr>
		</thead>
		<tbody>
			{#each data.org.members as member}
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
					<td class="px-6 py-4">
						{#if data.isAdmin && member.role !== 'OWNER' && member.user.id !== data.user.id}
							<form method="POST" action="?/updateRole" use:enhance class="inline">
								<input type="hidden" name="user_id" value={member.user.id} />
								<select
									name="role"
									class="h-8 rounded-lg border border-surface-200 bg-white px-2 text-sm transition-colors hover:border-surface-300"
									onchange={(e) => e.currentTarget.form?.requestSubmit()}
								>
									<option value="admin" selected={member.role === 'ADMIN'}>관리자</option>
									<option value="member" selected={member.role === 'MEMBER'}>멤버</option>
								</select>
							</form>
						{:else}
							<Badge
								variant={member.role === 'OWNER'
									? 'danger'
									: member.role === 'ADMIN'
										? 'warning'
										: 'default'}
								dot
							>
								{roleLabels[member.role]}
							</Badge>
						{/if}
					</td>
					<td class="px-6 py-4 text-sm text-surface-500">
						{new Date(member.joinedAt).toLocaleDateString('ko-KR')}
					</td>
					{#if data.isAdmin}
						<td class="px-6 py-4">
							{#if member.role !== 'OWNER' && member.user.id !== data.user.id}
								<form method="POST" action="?/remove" use:enhance>
									<input type="hidden" name="user_id" value={member.user.id} />
									<Button type="submit" variant="ghost" size="sm">제거</Button>
								</form>
							{/if}
						</td>
					{/if}
				</tr>
			{/each}
		</tbody>
	</table>
</section>
