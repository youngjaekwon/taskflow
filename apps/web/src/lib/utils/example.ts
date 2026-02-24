export function add(a: number, b: number): number {
	return a + b;
}

export function formatTaskId(id: number): string {
	return `TASK-${String(id).padStart(4, '0')}`;
}
