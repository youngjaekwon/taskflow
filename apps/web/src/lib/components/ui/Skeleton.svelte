<script lang="ts">
	interface Props {
		class?: string;
		width?: string;
		height?: string;
	}

	let { class: className = '', width, height }: Props = $props();
</script>

<div
	class="skeleton {className}"
	style:width={width}
	style:height={height}
	aria-hidden="true"
></div>
