import { fail, redirect } from '@sveltejs/kit';
import { register } from '$lib/server/auth';
import type { Actions } from './$types';

export const actions: Actions = {
	default: async ({ request, fetch }) => {
		const formData = await request.formData();
		const email = formData.get('email') as string;
		const password = formData.get('password') as string;
		const passwordConfirm = formData.get('password_confirm') as string;

		if (!email) return fail(400, { email, error: '이메일을 입력하세요.' });
		if (!password) return fail(400, { email, error: '비밀번호를 입력하세요.' });
		if (password !== passwordConfirm) {
			return fail(400, { email, error: '비밀번호가 일치하지 않습니다.' });
		}

		try {
			await register(fetch, email, password, passwordConfirm);
		} catch (e) {
			const message = e instanceof Error ? e.message : '회원가입에 실패했습니다.';
			return fail(400, { email, error: message });
		}

		redirect(303, '/register/success');
	}
};
