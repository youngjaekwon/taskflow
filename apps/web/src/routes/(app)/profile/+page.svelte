<script lang="ts">
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Avatar from '$lib/components/ui/Avatar.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import PageHeader from '$lib/components/layout/PageHeader.svelte';

	let { data, form }: PageProps = $props();
</script>

<svelte:head>
	<title>프로필 - TaskFlow</title>
</svelte:head>

<div class="mx-auto max-w-2xl p-6">
	<PageHeader title="프로필" />

	{#if form?.success}
		<div class="mb-6">
			<Alert variant="success">
				{#if form.action === 'profile'}프로필이 수정되었습니다.
				{:else if form.action === 'password'}비밀번호가 변경되었습니다.
				{:else if form.action === 'image'}프로필 이미지가 업로드되었습니다.
				{:else if form.action === 'imageDelete'}프로필 이미지가 삭제되었습니다.
				{/if}
			</Alert>
		</div>
	{/if}

	{#if form?.error}
		<div class="mb-6"><Alert variant="error">{form.error}</Alert></div>
	{/if}

	<!-- 프로필 이미지 -->
	<section class="mb-8 rounded-xl border border-surface-200/60 bg-white p-6 shadow-card">
		<h2 class="mb-4 text-base font-semibold text-surface-900">프로필 이미지</h2>
		<div class="flex items-center gap-6">
			<Avatar
				src={data.profile.profileImage}
				alt="{data.profile.firstName} {data.profile.lastName}"
				size="lg"
			/>
			<div class="flex gap-2">
				<form method="POST" action="?/uploadImage" enctype="multipart/form-data" use:enhance>
					<label class="inline-flex h-9 cursor-pointer items-center rounded-lg bg-brand-600 px-4 text-sm font-medium text-white transition-colors hover:bg-brand-700">
						이미지 변경
						<input type="file" name="image" accept="image/jpeg,image/png" class="hidden" onchange={(e) => e.currentTarget.form?.requestSubmit()} />
					</label>
				</form>
				{#if data.profile.profileImage}
					<form method="POST" action="?/deleteImage" use:enhance>
						<Button type="submit" variant="danger" size="sm">삭제</Button>
					</form>
				{/if}
			</div>
		</div>
	</section>

	<!-- 프로필 정보 -->
	<section class="mb-8 rounded-xl border border-surface-200/60 bg-white p-6 shadow-card">
		<h2 class="mb-4 text-base font-semibold text-surface-900">기본 정보</h2>
		<form method="POST" action="?/updateProfile" use:enhance class="space-y-4">
			<div class="text-sm">
				<span class="font-medium text-surface-500">이메일</span>
				<p class="mt-1 text-surface-900">{data.profile.email}</p>
			</div>
			<Input
				id="first_name"
				name="first_name"
				label="이름"
				value={data.profile.firstName}
			/>
			<Input
				id="last_name"
				name="last_name"
				label="성"
				value={data.profile.lastName}
			/>
			<Button type="submit">저장</Button>
		</form>
	</section>

	<!-- 비밀번호 변경 -->
	<section class="rounded-xl border border-surface-200/60 bg-white p-6 shadow-card">
		<h2 class="mb-4 text-base font-semibold text-surface-900">비밀번호 변경</h2>
		<form method="POST" action="?/changePassword" use:enhance class="space-y-4">
			<Input
				id="old_password"
				name="old_password"
				type="password"
				label="현재 비밀번호"
				required
				autocomplete="current-password"
			/>
			<Input
				id="new_password"
				name="new_password"
				type="password"
				label="새 비밀번호"
				required
				autocomplete="new-password"
			/>
			<Input
				id="new_password_confirm"
				name="new_password_confirm"
				type="password"
				label="새 비밀번호 확인"
				required
				autocomplete="new-password"
			/>
			<Button type="submit">비밀번호 변경</Button>
		</form>
	</section>
</div>
