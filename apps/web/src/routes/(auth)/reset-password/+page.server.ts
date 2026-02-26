import { fail, redirect } from '@sveltejs/kit';
import { confirmPasswordReset } from '$lib/server/auth';
import type { PageServerLoad, Actions } from './$types';

export const load: PageServerLoad = async ({ url }) => {
	const uid = url.searchParams.get('uid');
	const token = url.searchParams.get('token');

	return { uid, token };
};

export const actions: Actions = {
	default: async ({ request, fetch }) => {
		const formData = await request.formData();
		const uid = formData.get('uid') as string;
		const token = formData.get('token') as string;
		const newPassword = formData.get('new_password') as string;
		const newPasswordConfirm = formData.get('new_password_confirm') as string;

		if (!newPassword) return fail(400, { error: '새 비밀번호를 입력하세요.' });
		if (newPassword !== newPasswordConfirm) {
			return fail(400, { error: '비밀번호가 일치하지 않습니다.' });
		}

		try {
			await confirmPasswordReset(fetch, uid, token, newPassword, newPasswordConfirm);
		} catch (e) {
			const message = e instanceof Error ? e.message : '비밀번호 초기화에 실패했습니다.';
			return fail(400, { error: message });
		}

		redirect(303, '/login?reset=success');
	}
};
