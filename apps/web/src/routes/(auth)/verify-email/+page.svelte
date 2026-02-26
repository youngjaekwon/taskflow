<script lang="ts">
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';

	let { data, form }: PageProps = $props();
</script>

<svelte:head>
	<title>이메일 인증 - TaskFlow</title>
</svelte:head>

<div class="space-y-6 text-center">
	{#if data.verified}
		<div class="mx-auto flex h-14 w-14 items-center justify-center rounded-xl bg-success-50">
			<svg class="h-7 w-7 text-success-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
			</svg>
		</div>
		<h1 class="text-xl font-semibold text-surface-900">이메일 인증 완료</h1>
		<p class="text-sm text-surface-500">{data.message}</p>
		<a href="/login" class="inline-block text-sm text-brand-600 hover:text-brand-700">로그인 페이지로 이동</a>
	{:else}
		<h1 class="text-xl font-semibold text-surface-900">이메일 인증</h1>

		{#if data.message}
			<Alert variant="error">{data.message}</Alert>
		{/if}

		{#if form?.sent}
			<Alert variant="success">인증 메일이 발송되었습니다. 이메일을 확인하세요.</Alert>
		{/if}

		<p class="text-sm text-surface-500">인증 이메일을 다시 받으시려면 이메일 주소를 입력하세요.</p>

		<form method="POST" action="?/resend" use:enhance class="space-y-4 text-left">
			<Input id="email" name="email" type="email" label="이메일" required />
			<Button type="submit" class="w-full">인증 메일 재발송</Button>
		</form>
	{/if}
</div>
