<script lang="ts">
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';

	let { data, form }: PageProps = $props();
</script>

<svelte:head>
	<title>비밀번호 재설정 - TaskFlow</title>
</svelte:head>

<div class="space-y-6">
	<div class="text-center">
		<h1 class="text-xl font-semibold text-surface-900">비밀번호 재설정</h1>
		<p class="mt-1 text-sm text-surface-500">새 비밀번호를 입력하세요.</p>
	</div>

	{#if !data.uid || !data.token}
		<Alert variant="error">
			유효하지 않은 링크입니다. <a href="/forgot-password" class="underline">다시 요청하세요.</a>
		</Alert>
	{:else}
		{#if form?.error}
			<Alert variant="error">{form.error}</Alert>
		{/if}

		<form method="POST" use:enhance class="space-y-4">
			<input type="hidden" name="uid" value={data.uid} />
			<input type="hidden" name="token" value={data.token} />
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
			<Button type="submit" class="w-full">비밀번호 재설정</Button>
		</form>
	{/if}
</div>
