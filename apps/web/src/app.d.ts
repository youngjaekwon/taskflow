// See https://svelte.dev/docs/kit/types#app
declare global {
	namespace App {
		interface Error {
			message: string;
			errorId?: string;
		}
		interface Locals {
			user: {
				id: string;
				email: string;
				username: string;
				firstName: string;
				lastName: string;
				profileImage: string | null;
			} | null;
			accessToken: string | null;
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
