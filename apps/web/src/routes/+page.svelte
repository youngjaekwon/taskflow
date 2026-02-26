<script lang="ts">
	import type { PageProps } from './$types';
	import Button from '$lib/components/ui/Button.svelte';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title>TaskFlow</title>
</svelte:head>

<main class="relative flex flex-col items-center justify-center min-h-[calc(100vh-3.5rem)] overflow-hidden bg-surface-50 px-4">
	<!-- 배경 그라디언트 -->
	<div class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,var(--color-brand-100)_0%,transparent_60%)]"></div>

	<div class="relative z-10 flex flex-col items-center gap-8">
		<!-- Announcement pill -->
		<span class="inline-flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-4 py-1.5 text-sm font-medium text-brand-700">
			<span class="h-1.5 w-1.5 rounded-full bg-brand-500"></span>
			GraphQL 기반 태스크 관리 앱
		</span>

		<!-- 헤드라인 -->
		<h1 class="max-w-2xl text-center text-5xl font-bold leading-tight tracking-tight text-surface-900">
			팀의 업무를 <span class="text-brand-600">체계적으로</span> 관리하세요
		</h1>

		<p class="max-w-md text-center text-lg text-surface-500">
			칸반 보드, 태스크 추적, 팀 협업을 하나의 공간에서. 간단하고 직관적인 프로젝트 관리 도구.
		</p>

		{#if data.user}
			<div class="flex flex-col items-center gap-4">
				<p class="text-surface-600">
					환영합니다{#if data.user.firstName || data.user.email}, <span class="font-semibold text-surface-900">{data.user.firstName || data.user.email}</span>님{/if}!
				</p>
				<a href="/orgs">
					<Button size="lg">내 조직</Button>
				</a>
			</div>
		{:else}
			<div class="flex gap-3">
				<a href="/login">
					<Button variant="secondary" size="lg">로그인</Button>
				</a>
				<a href="/register">
					<Button size="lg">시작하기</Button>
				</a>
			</div>
		{/if}

		<!-- CSS-only 칸반 보드 프리뷰 -->
		<div class="mt-8 w-full max-w-2xl rounded-xl border border-surface-200/60 bg-white/60 p-4 shadow-card backdrop-blur-sm">
			<div class="flex gap-3">
				{#each ['To Do', 'In Progress', 'Done'] as col, i}
					<div class="flex-1 rounded-lg bg-surface-100/60 p-2.5">
						<div class="mb-2 flex items-center gap-1.5">
							<span class="h-2 w-2 rounded-full {i === 0 ? 'bg-surface-400' : i === 1 ? 'bg-brand-400' : 'bg-success-500'}"></span>
							<span class="text-xs font-semibold uppercase tracking-wider text-surface-400">{col}</span>
						</div>
						{#each Array(i === 1 ? 2 : i === 0 ? 3 : 1) as _}
							<div class="mb-1.5 rounded-md border border-surface-200/60 bg-white p-2.5">
								<div class="h-2 w-3/4 rounded skeleton"></div>
								<div class="mt-2 h-2 w-1/2 rounded skeleton"></div>
							</div>
						{/each}
					</div>
				{/each}
			</div>
		</div>
	</div>
</main>
