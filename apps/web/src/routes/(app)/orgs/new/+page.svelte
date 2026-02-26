<script lang="ts">
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Textarea from '$lib/components/ui/Textarea.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import PageHeader from '$lib/components/layout/PageHeader.svelte';

	let { form }: PageProps = $props();
</script>

<svelte:head>
	<title>새 조직 - TaskFlow</title>
</svelte:head>

<div class="mx-auto max-w-lg p-6">
	<PageHeader title="새 조직 만들기" />

	{#if form?.error}
		<div class="mb-6">
			<Alert variant="error">{form.error}</Alert>
		</div>
	{/if}

	<form method="POST" use:enhance class="space-y-4 rounded-xl border border-surface-200/60 bg-white p-6 shadow-card">
		<Input
			id="name"
			name="name"
			label="이름"
			value={form?.name ?? ''}
			required
			placeholder="조직 이름"
		/>
		<Textarea
			id="description"
			name="description"
			label="설명"
			rows={3}
			placeholder="조직 설명 (선택)"
			value={form?.description ?? ''}
		/>
		<div class="flex gap-2">
			<Button type="submit">생성</Button>
			<a href="/orgs">
				<Button type="button" variant="secondary">취소</Button>
			</a>
		</div>
	</form>
</div>
