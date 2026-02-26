export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
	id: string;
	message: string;
	variant: ToastVariant;
	duration: number;
}

const DEFAULT_DURATION: Record<ToastVariant, number> = {
	success: 5000,
	error: 8000,
	warning: 5000,
	info: 5000
};

let toasts = $state<Toast[]>([]);
const timers = new Map<string, ReturnType<typeof setTimeout>>();

export const toastStore = {
	get toasts() {
		return toasts;
	},

	add(message: string, variant: ToastVariant = 'info', duration?: number) {
		const id = crypto.randomUUID();
		const ms = duration ?? DEFAULT_DURATION[variant];
		const toast: Toast = { id, message, variant, duration: ms };
		toasts = [...toasts, toast];

		const timer = setTimeout(() => this.remove(id), ms);
		timers.set(id, timer);

		return id;
	},

	remove(id: string) {
		const timer = timers.get(id);
		if (timer) {
			clearTimeout(timer);
			timers.delete(id);
		}
		toasts = toasts.filter((t) => t.id !== id);
	},

	success(message: string, duration?: number) {
		return this.add(message, 'success', duration);
	},

	error(message: string, duration?: number) {
		return this.add(message, 'error', duration);
	},

	warning(message: string, duration?: number) {
		return this.add(message, 'warning', duration);
	},

	info(message: string, duration?: number) {
		return this.add(message, 'info', duration);
	}
};
