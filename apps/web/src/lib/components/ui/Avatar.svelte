<script lang="ts">
	interface Props {
		src?: string | null;
		alt?: string;
		size?: 'sm' | 'md' | 'lg';
		class?: string;
	}

	let { src, alt = '', size = 'md', class: className = '' }: Props = $props();

	const sizes = {
		sm: 'h-6 w-6 text-xs',
		md: 'h-8 w-8 text-sm',
		lg: 'h-12 w-12 text-base'
	};

	let initials = $derived(
		alt
			.split(' ')
			.map((w) => w[0])
			.join('')
			.toUpperCase()
			.slice(0, 2) || '?'
	);

	const colorPalette = [
		'bg-brand-100 text-brand-700',
		'bg-success-100 text-success-700',
		'bg-warning-100 text-warning-700',
		'bg-info-100 text-info-700',
		'bg-danger-100 text-danger-700'
	];

	let colorClass = $derived(() => {
		let hash = 0;
		for (let i = 0; i < alt.length; i++) {
			hash = alt.charCodeAt(i) + ((hash << 5) - hash);
		}
		return colorPalette[Math.abs(hash) % colorPalette.length];
	});
</script>

{#if src}
	<img {src} {alt} class="rounded-full object-cover ring-2 ring-white {sizes[size]} {className}" />
{:else}
	<div
		class="flex items-center justify-center rounded-full font-medium ring-2 ring-white {sizes[size]} {colorClass()} {className}"
	>
		{initials}
	</div>
{/if}
