import { describe, it, expect } from 'vitest';
import { add, formatTaskId } from './example';

describe('add', () => {
	it('adds two numbers', () => {
		expect(add(1, 2)).toBe(3);
	});

	it('handles negative numbers', () => {
		expect(add(-1, 1)).toBe(0);
	});
});

describe('formatTaskId', () => {
	it('pads single digit id', () => {
		expect(formatTaskId(1)).toBe('TASK-0001');
	});

	it('preserves four digit id', () => {
		expect(formatTaskId(1234)).toBe('TASK-1234');
	});
});
