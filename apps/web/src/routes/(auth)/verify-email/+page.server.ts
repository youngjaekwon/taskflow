import { fail } from '@sveltejs/kit';
import { verifyEmail, resendVerificationEmail } from '$lib/server/auth';
import type { PageServerLoad, Actions } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const uid = url.searchParams.get('uid');
	const token = url.searchParams.get('token');

	if (uid && token) {
		try {
			const result = await verifyEmail(fetch, uid, token);
			return { verified: true, message: result.detail };
		} catch (e) {
			const message = e instanceof Error ? e.message : '인증에 실패했습니다.';
			return { verified: false, message };
		}
	}

	return { verified: false, message: null };
};

export const actions: Actions = {
	resend: async ({ request, fetch }) => {
		const formData = await request.formData();
		const email = formData.get('email') as string;

		if (!email) return fail(400, { error: '이메일을 입력하세요.' });

		try {
			await resendVerificationEmail(fetch, email);
		} catch {
			// 보안: 이메일 존재 여부와 관계없이 동일한 메시지
		}

		return { sent: true };
	}
};
