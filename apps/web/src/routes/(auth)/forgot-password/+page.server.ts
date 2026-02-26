import { fail } from '@sveltejs/kit';
import { requestPasswordReset } from '$lib/server/auth';
import type { Actions } from './$types';

export const actions: Actions = {
	default: async ({ request, fetch }) => {
		const formData = await request.formData();
		const email = formData.get('email') as string;

		if (!email) return fail(400, { error: '이메일을 입력하세요.' });

		try {
			await requestPasswordReset(fetch, email);
		} catch {
			// 보안: 이메일 존재 여부와 관계없이 동일한 메시지
		}

		return { sent: true };
	}
};
