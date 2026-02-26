<script lang="ts">
	import { page } from '$app/state';
	import Button from '$lib/components/ui/Button.svelte';
</script>

<svelte:head>
	<title>오류 - TaskFlow</title>
</svelte:head>

<main class="flex min-h-[calc(100vh-3.5rem)] items-center justify-center bg-surface-50 px-4">
	<div class="flex flex-col items-center text-center">
		<div class="flex h-20 w-20 items-center justify-center rounded-2xl bg-surface-100 text-surface-300">
			<span class="text-3xl font-bold">{page.status}</span>
		</div>
		<h1 class="mt-6 text-xl font-semibold text-surface-900">
			{#if page.status === 403}
				접근 권한이 없습니다
			{:else if page.status === 404}
				페이지를 찾을 수 없습니다
			{:else}
				오류가 발생했습니다
			{/if}
		</h1>
		<p class="mt-2 max-w-sm text-sm text-surface-500">{page.error?.message}</p>
		<div class="mt-6">
			<a href="/">
				<Button variant="secondary">홈으로 돌아가기</Button>
			</a>
		</div>
	</div>
</main>
