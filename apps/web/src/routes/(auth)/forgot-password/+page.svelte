<script lang="ts">
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';

	let { form }: PageProps = $props();
</script>

<svelte:head>
	<title>비밀번호 찾기 - TaskFlow</title>
</svelte:head>

<div class="space-y-6">
	<div class="text-center">
		<h1 class="text-xl font-semibold text-surface-900">비밀번호 찾기</h1>
		<p class="mt-1 text-sm text-surface-500">
			가입하신 이메일 주소를 입력하시면 비밀번호 초기화 링크를 보내드립니다.
		</p>
	</div>

	{#if form?.sent}
		<Alert variant="success">비밀번호 초기화 메일이 발송되었습니다. 이메일을 확인하세요.</Alert>
	{/if}

	{#if form?.error}
		<Alert variant="error">{form.error}</Alert>
	{/if}

	<form method="POST" use:enhance class="space-y-4">
		<Input id="email" name="email" type="email" label="이메일" required />
		<Button type="submit" class="w-full">초기화 링크 발송</Button>
	</form>

	<p class="text-center text-sm text-surface-500">
		<a href="/login" class="text-brand-600 hover:text-brand-700">로그인으로 돌아가기</a>
	</p>
</div>
