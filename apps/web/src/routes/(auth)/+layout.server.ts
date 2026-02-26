import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
	// 이미 로그인된 사용자는 앱으로 리다이렉트
	if (locals.user) {
		redirect(302, '/orgs');
	}
};
