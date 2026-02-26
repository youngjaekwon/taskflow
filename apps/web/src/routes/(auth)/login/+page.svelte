<script lang="ts">
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';

	let { form }: PageProps = $props();
</script>

<svelte:head>
	<title>로그인 - TaskFlow</title>
</svelte:head>

<div class="space-y-6">
	<div class="text-center">
		<h1 class="text-xl font-semibold text-surface-900">로그인</h1>
		<p class="mt-1 text-sm text-surface-500">TaskFlow에 로그인하세요</p>
	</div>

	{#if form?.error}
		<Alert variant="error">{form.error}</Alert>
	{/if}

	<form method="POST" use:enhance class="space-y-4">
		<Input
			id="email"
			name="email"
			type="email"
			label="이메일"
			value={form?.email ?? ''}
			required
			autocomplete="email"
			validate={(v) => {
				if (!v) return '이메일을 입력하세요.';
				if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return '올바른 이메일 형식이 아닙니다.';
				return null;
			}}
		/>
		<Input
			id="password"
			name="password"
			type="password"
			label="비밀번호"
			required
			autocomplete="current-password"
		/>
		<Button type="submit" class="w-full">로그인</Button>
	</form>

	<div class="flex justify-between text-sm">
		<a href="/forgot-password" class="text-brand-600 hover:text-brand-700">비밀번호를 잊으셨나요?</a>
		<a href="/register" class="text-brand-600 hover:text-brand-700">회원가입</a>
	</div>
</div>
