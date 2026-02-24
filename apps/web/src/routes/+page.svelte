<script lang="ts">
	let count = $state(0);
	let doubled = $derived(count * 2);
</script>

<svelte:head>
	<title>TaskFlow</title>
</svelte:head>

<main class="flex flex-col items-center justify-center min-h-screen gap-6">
	<h1 class="text-4xl font-bold">TaskFlow</h1>
	<p class="text-gray-600">GraphQL 기반 태스크 관리 앱</p>

	<div class="flex flex-col items-center gap-2 p-6 bg-white rounded-lg shadow">
		<p class="text-lg">카운터: <span class="font-mono font-bold">{count}</span></p>
		<p class="text-sm text-gray-500">x2 = {doubled}</p>
		<div class="flex gap-2 mt-2">
			<button
				class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
				onclick={() => (count -= 1)}
			>
				-1
			</button>
			<button
				class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
				onclick={() => (count += 1)}
			>
				+1
			</button>
		</div>
	</div>

	<nav class="flex gap-4 mt-4">
		<a href="/boards" class="text-blue-500 hover:underline">보드 목록</a>
	</nav>
</main>
