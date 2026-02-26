import { AUTH_API_BASE } from '$env/static/private';
import type { LoginResponse, TokenRefreshResponse } from '$lib/types';

type FetchFn = typeof globalThis.fetch;

async function authRequest<T>(
	fetchFn: FetchFn,
	path: string,
	body: Record<string, unknown>,
	token?: string
): Promise<T> {
	const headers: Record<string, string> = { 'Content-Type': 'application/json' };
	if (token) headers['Authorization'] = `Bearer ${token}`;

	const response = await fetchFn(`${AUTH_API_BASE}${path}`, {
		method: 'POST',
		headers,
		body: JSON.stringify(body)
	});

	if (!response.ok) {
		const data = await response.json().catch(() => ({}));
		const message =
			data.detail || Object.values(data).flat().join(', ') || `Request failed: ${response.status}`;
		const error = new Error(message) as Error & { status: number; data: unknown };
		error.status = response.status;
		error.data = data;
		throw error;
	}

	if (response.status === 204) return {} as T;
	return response.json();
}

export async function register(
	fetchFn: FetchFn,
	email: string,
	password: string,
	passwordConfirm: string
) {
	return authRequest<{ detail: string }>(fetchFn, '/auth/register/', {
		email,
		password,
		password_confirm: passwordConfirm
	});
}

export async function login(fetchFn: FetchFn, email: string, password: string) {
	return authRequest<LoginResponse>(fetchFn, '/auth/login/', { email, password });
}

export async function logout(fetchFn: FetchFn, refreshToken: string) {
	return authRequest<{ detail: string }>(fetchFn, '/auth/logout/', { refresh: refreshToken });
}

export async function refreshTokens(fetchFn: FetchFn, refreshToken: string) {
	return authRequest<TokenRefreshResponse>(fetchFn, '/auth/token/refresh/', {
		refresh: refreshToken
	});
}

export async function verifyEmail(fetchFn: FetchFn, uid: string, token: string) {
	return authRequest<{ detail: string }>(fetchFn, '/auth/email/verify/', { uid, token });
}

export async function resendVerificationEmail(fetchFn: FetchFn, email: string) {
	return authRequest<{ detail: string }>(fetchFn, '/auth/email/resend/', { email });
}

export async function requestPasswordReset(fetchFn: FetchFn, email: string) {
	return authRequest<{ detail: string }>(fetchFn, '/auth/password/reset/', { email });
}

export async function confirmPasswordReset(
	fetchFn: FetchFn,
	uid: string,
	token: string,
	newPassword: string,
	newPasswordConfirm: string
) {
	return authRequest<{ detail: string }>(fetchFn, '/auth/password/reset/confirm/', {
		uid,
		token,
		new_password: newPassword,
		new_password_confirm: newPasswordConfirm
	});
}

export async function changePassword(
	fetchFn: FetchFn,
	accessToken: string,
	oldPassword: string,
	newPassword: string,
	newPasswordConfirm: string
) {
	return authRequest<{ detail: string; access: string; refresh: string }>(
		fetchFn,
		'/auth/password/change/',
		{
			old_password: oldPassword,
			new_password: newPassword,
			new_password_confirm: newPasswordConfirm
		},
		accessToken
	);
}

export async function uploadProfileImage(fetchFn: FetchFn, accessToken: string, image: File) {
	const formData = new FormData();
	formData.append('image', image);

	const response = await fetchFn(`${AUTH_API_BASE}/users/me/profile-image/`, {
		method: 'PUT',
		headers: { Authorization: `Bearer ${accessToken}` },
		body: formData
	});

	if (!response.ok) {
		const data = await response.json().catch(() => ({}));
		const error = new Error(data.detail || 'Upload failed') as Error & {
			status: number;
			data: unknown;
		};
		error.status = response.status;
		error.data = data;
		throw error;
	}

	return response.json() as Promise<{ detail: string; profile_image_url: string }>;
}

export async function deleteProfileImage(fetchFn: FetchFn, accessToken: string) {
	const response = await fetchFn(`${AUTH_API_BASE}/users/me/profile-image/`, {
		method: 'DELETE',
		headers: { Authorization: `Bearer ${accessToken}` }
	});

	if (!response.ok) {
		const data = await response.json().catch(() => ({}));
		const error = new Error(data.detail || 'Delete failed') as Error & {
			status: number;
			data: unknown;
		};
		error.status = response.status;
		error.data = data;
		throw error;
	}
}
