import { fail, redirect } from '@sveltejs/kit';
import { login } from '$lib/server/auth';
import { setAuthCookies } from '$lib/server/cookies';
import type { Actions } from './$types';

export const actions: Actions = {
	default: async ({ request, fetch, cookies, url }) => {
		const formData = await request.formData();
		const email = formData.get('email') as string;
		const password = formData.get('password') as string;

		if (!email) return fail(400, { email, error: '이메일을 입력하세요.' });
		if (!password) return fail(400, { email, error: '비밀번호를 입력하세요.' });

		try {
			const result = await login(fetch, email, password);
			setAuthCookies(cookies, result);
		} catch (e) {
			const message = e instanceof Error ? e.message : '로그인에 실패했습니다.';
			return fail(400, { email, error: message });
		}

		const redirectTo = url.searchParams.get('redirect') || '/orgs';
		const safeRedirect = redirectTo.startsWith('/') && !redirectTo.startsWith('//') ? redirectTo : '/orgs';
		redirect(303, safeRedirect);
	}
};
