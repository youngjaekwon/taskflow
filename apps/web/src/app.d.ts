// See https://svelte.dev/docs/kit/types#app
declare global {
	namespace App {
		interface Error {
			message: string;
			errorId?: string;
		}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
