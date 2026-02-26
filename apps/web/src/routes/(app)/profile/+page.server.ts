import { fail, redirect } from '@sveltejs/kit';
import { graphqlRequest } from '$lib/server/graphql';
import { changePassword, uploadProfileImage, deleteProfileImage } from '$lib/server/auth';
import { setAuthCookies } from '$lib/server/cookies';
import { ME_QUERY } from '$lib/graphql/queries/user';
import { UPDATE_PROFILE_MUTATION } from '$lib/graphql/mutations/user';
import type { PageServerLoad, Actions } from './$types';
import type { User } from '$lib/types';

export const load: PageServerLoad = async ({ locals, fetch }) => {
	if (!locals.accessToken) redirect(302, '/login');

	const data = await graphqlRequest<{ me: User }>(fetch, ME_QUERY, {}, locals.accessToken);
	return { profile: data.me };
};

export const actions: Actions = {
	updateProfile: async ({ request, fetch, locals }) => {
		if (!locals.accessToken) redirect(302, '/login');
		const formData = await request.formData();
		const firstName = formData.get('first_name') as string;
		const lastName = formData.get('last_name') as string;

		try {
			await graphqlRequest(
				fetch,
				UPDATE_PROFILE_MUTATION,
				{ input: { firstName, lastName } },
				locals.accessToken
			);
			return { success: true, action: 'profile' };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '프로필 수정에 실패했습니다.' });
		}
	},

	uploadImage: async ({ request, fetch, locals }) => {
		if (!locals.accessToken) redirect(302, '/login');
		const formData = await request.formData();
		const image = formData.get('image') as File;

		if (!image || image.size === 0) {
			return fail(400, { error: '이미지를 선택하세요.' });
		}
		if (image.size > 5 * 1024 * 1024) {
			return fail(400, { error: '이미지 크기는 5MB 이하여야 합니다.' });
		}

		try {
			await uploadProfileImage(fetch, locals.accessToken, image);
			return { success: true, action: 'image' };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '이미지 업로드에 실패했습니다.' });
		}
	},

	deleteImage: async ({ fetch, locals }) => {
		if (!locals.accessToken) redirect(302, '/login');

		try {
			await deleteProfileImage(fetch, locals.accessToken);
			return { success: true, action: 'imageDelete' };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '이미지 삭제에 실패했습니다.' });
		}
	},

	changePassword: async ({ request, fetch, locals, cookies }) => {
		if (!locals.accessToken) redirect(302, '/login');
		const formData = await request.formData();
		const oldPassword = formData.get('old_password') as string;
		const newPassword = formData.get('new_password') as string;
		const newPasswordConfirm = formData.get('new_password_confirm') as string;

		if (!oldPassword || !newPassword) {
			return fail(400, { error: '모든 필드를 입력하세요.' });
		}
		if (newPassword !== newPasswordConfirm) {
			return fail(400, { error: '새 비밀번호가 일치하지 않습니다.' });
		}

		try {
			const result = await changePassword(
				fetch,
				locals.accessToken,
				oldPassword,
				newPassword,
				newPasswordConfirm
			);

			// 새 토큰으로 쿠키 업데이트
			setAuthCookies(cookies, result);

			return { success: true, action: 'password' };
		} catch (e) {
			return fail(400, { error: e instanceof Error ? e.message : '비밀번호 변경에 실패했습니다.' });
		}
	}
};
