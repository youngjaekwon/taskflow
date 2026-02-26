import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals, url }) => {
	if (!locals.user || !locals.accessToken) {
		const redirectTo = url.pathname + url.search;
		redirect(302, `/login?redirect=${encodeURIComponent(redirectTo)}`);
	}

	return {
		user: locals.user,
		accessToken: locals.accessToken
	};
};
