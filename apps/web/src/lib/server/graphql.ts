import { GRAPHQL_ENDPOINT } from '$env/static/private';
import { error } from '@sveltejs/kit';

interface GraphQLResponse<T> {
	data: T;
	errors?: Array<{ message: string; extensions?: { code?: string } }>;
}

export async function graphqlRequest<T>(
	fetch: typeof globalThis.fetch,
	query: string,
	variables?: Record<string, unknown>,
	accessToken?: string | null
): Promise<T> {
	const headers: Record<string, string> = { 'Content-Type': 'application/json' };
	if (accessToken) {
		headers['Authorization'] = `Bearer ${accessToken}`;
	}

	const response = await fetch(GRAPHQL_ENDPOINT, {
		method: 'POST',
		headers,
		body: JSON.stringify({ query, variables })
	});

	if (!response.ok) {
		if (response.status === 401) {
			error(401, '인증이 필요합니다.');
		}
		throw new Error(`GraphQL request failed: ${response.status} ${response.statusText}`);
	}

	const result: GraphQLResponse<T> = await response.json();

	if (result.errors && result.errors.length > 0) {
		const err = result.errors[0];
		const code = err.extensions?.code;
		const message = err.message;

		// extensions.code 우선 확인
		if (code === 'FORBIDDEN') error(403, '접근 권한이 없습니다.');
		if (code === 'NOT_FOUND') error(404, '리소스를 찾을 수 없습니다.');
		if (code === 'UNAUTHENTICATED') error(401, '인증이 필요합니다.');

		// 폴백: 메시지 기반 매칭
		const lowerMessage = message.toLowerCase();
		if (lowerMessage.includes('permission') || message.includes('권한')) {
			error(403, '접근 권한이 없습니다.');
		}
		if (lowerMessage.includes('not found') || message.includes('찾을 수 없')) {
			error(404, '리소스를 찾을 수 없습니다.');
		}
		if (lowerMessage.includes('authentication') || message.includes('인증')) {
			error(401, '인증이 필요합니다.');
		}

		throw new Error(message);
	}

	return result.data;
}
