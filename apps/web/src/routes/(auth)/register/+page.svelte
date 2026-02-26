<script lang="ts">
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';

	let { form }: PageProps = $props();
</script>

<svelte:head>
	<title>회원가입 - TaskFlow</title>
</svelte:head>

<div class="space-y-6">
	<div class="text-center">
		<h1 class="text-xl font-semibold text-surface-900">회원가입</h1>
		<p class="mt-1 text-sm text-surface-500">TaskFlow 계정을 만드세요</p>
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
			autocomplete="new-password"
			hint="8자 이상 입력하세요"
			validate={(v) => {
				if (!v) return '비밀번호를 입력하세요.';
				if (v.length < 8) return '비밀번호는 8자 이상이어야 합니다.';
				return null;
			}}
			validateOn="input"
		/>
		<Input
			id="password_confirm"
			name="password_confirm"
			type="password"
			label="비밀번호 확인"
			required
			autocomplete="new-password"
			validate={(v) => {
				if (!v) return '비밀번호 확인을 입력하세요.';
				const pwInput = document.getElementById('password') as HTMLInputElement;
				if (pwInput && v !== pwInput.value) return '비밀번호가 일치하지 않습니다.';
				return null;
			}}
		/>
		<Button type="submit" class="w-full">회원가입</Button>
	</form>

	<p class="text-center text-sm text-surface-500">
		이미 계정이 있나요? <a href="/login" class="text-brand-600 hover:text-brand-700">로그인</a>
	</p>
</div>
