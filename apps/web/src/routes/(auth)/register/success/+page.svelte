<svelte:head>
	<title>이메일 확인 - TaskFlow</title>
</svelte:head>

<div class="space-y-6 text-center">
	<div class="mx-auto flex h-14 w-14 items-center justify-center rounded-xl bg-success-50">
		<svg class="h-7 w-7 text-success-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
		</svg>
	</div>
	<h1 class="text-xl font-semibold text-surface-900">이메일을 확인하세요</h1>
	<p class="text-sm text-surface-500">
		회원가입이 완료되었습니다. 입력하신 이메일로 인증 링크가 발송되었습니다.
		이메일을 확인하여 계정을 활성화하세요.
	</p>
	<a href="/login" class="inline-block text-sm text-brand-600 hover:text-brand-700">로그인 페이지로 이동</a>
</div>
