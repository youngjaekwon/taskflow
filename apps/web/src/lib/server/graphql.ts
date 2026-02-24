import { GRAPHQL_ENDPOINT } from '$env/static/private';

export async function graphqlRequest<T>(
	fetch: typeof globalThis.fetch,
	query: string,
	variables?: Record<string, unknown>
): Promise<T> {
	const response = await fetch(GRAPHQL_ENDPOINT, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ query, variables })
	});

	if (!response.ok) {
		throw new Error(`GraphQL request failed: ${response.status} ${response.statusText}`);
	}

	const { data, errors } = await response.json();
	if (errors) throw new Error(errors[0].message);
	return data as T;
}
