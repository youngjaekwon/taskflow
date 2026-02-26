<script lang="ts">
	import Modal from './Modal.svelte';
	import Button from './Button.svelte';

	interface Props {
		open: boolean;
		title: string;
		description?: string;
		confirmLabel?: string;
		cancelLabel?: string;
		variant?: 'danger' | 'warning';
		loading?: boolean;
		onconfirm: () => void;
		oncancel: () => void;
	}

	let {
		open,
		title,
		description,
		confirmLabel = '확인',
		cancelLabel = '취소',
		variant = 'danger',
		loading = false,
		onconfirm,
		oncancel
	}: Props = $props();
</script>

<Modal {open} onclose={oncancel} {title} {description} size="sm">
	{#snippet children()}
		<div class="flex justify-end gap-2">
			<Button type="button" variant="secondary" onclick={oncancel} disabled={loading}>
				{cancelLabel}
			</Button>
			<Button
				type="button"
				variant={variant === 'danger' ? 'danger' : 'primary'}
				onclick={onconfirm}
				{loading}
			>
				{confirmLabel}
			</Button>
		</div>
	{/snippet}
</Modal>
