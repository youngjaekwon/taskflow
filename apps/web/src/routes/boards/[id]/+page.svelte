<script lang="ts">
	import { page } from '$app/state';
</script>

<svelte:head>
	<title>보드 {page.params.id} — TaskFlow</title>
</svelte:head>

<main class="max-w-4xl mx-auto p-8">
	<h1 class="text-2xl font-bold mb-4">보드 #{page.params.id}</h1>
	<p class="text-gray-500">백엔드 연동 후 구현 예정</p>
	<a href="/boards" class="text-blue-500 hover:underline mt-4 inline-block">← 보드 목록</a>
</main>
