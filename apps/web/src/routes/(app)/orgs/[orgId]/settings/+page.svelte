<script lang="ts">
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Textarea from '$lib/components/ui/Textarea.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import PageHeader from '$lib/components/layout/PageHeader.svelte';
	import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
	import { toastStore } from '$lib/stores/toast.svelte';

	let { data, form }: PageProps = $props();
	let showDeleteConfirm = $state(false);
	let deleting = $state(false);
</script>

<svelte:head>
	<title>기본정보 - {data.org.name} - TaskFlow</title>
</svelte:head>

<PageHeader title="기본정보" />

{#if form?.success}
	<div class="mb-6"><Alert variant="success">수정되었습니다.</Alert></div>
{/if}
{#if form?.error}
	<div class="mb-6"><Alert variant="error">{form.error}</Alert></div>
{/if}

<section class="mb-8 rounded-xl border border-surface-200/60 bg-white p-6 shadow-card">
	<h2 class="mb-4 text-base font-semibold text-surface-900">기본 정보</h2>
	{#if data.isAdmin}
		<form method="POST" action="?/update" use:enhance class="space-y-4">
			<Input id="name" name="name" label="이름" value={data.org.name} required />
			<Textarea
				id="description"
				name="description"
				label="설명"
				rows={3}
				value={data.org.description}
			/>
			<Button type="submit">저장</Button>
		</form>
	{:else}
		<dl class="space-y-4">
			<div>
				<dt class="text-sm font-medium text-surface-500">이름</dt>
				<dd class="mt-1 text-surface-900">{data.org.name}</dd>
			</div>
			<div>
				<dt class="text-sm font-medium text-surface-500">설명</dt>
				<dd class="mt-1 text-surface-700">{data.org.description || '(없음)'}</dd>
			</div>
		</dl>
	{/if}
</section>

{#if data.isOwner}
	<section class="rounded-xl border border-danger-100 bg-white p-6 shadow-card">
		<h2 class="mb-4 text-base font-semibold text-danger-700">위험 영역</h2>
		<Button variant="danger" onclick={() => (showDeleteConfirm = true)}>
			조직 삭제
		</Button>
	</section>

	<ConfirmDialog
		open={showDeleteConfirm}
		title="조직 삭제"
		description="정말로 {data.org.name}을(를) 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다."
		confirmLabel="삭제"
		variant="danger"
		loading={deleting}
		onconfirm={async () => {
			deleting = true;
			const formData = new FormData();
			await fetch('?/delete', { method: 'POST', body: formData });
			deleting = false;
			showDeleteConfirm = false;
			toastStore.success('조직이 삭제되었습니다.');
		}}
		oncancel={() => (showDeleteConfirm = false)}
	/>
{/if}
