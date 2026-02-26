let open = $state(false);

export const sidebarStore = {
	get open() {
		return open;
	},

	toggle() {
		open = !open;
	},

	show() {
		open = true;
	},

	hide() {
		open = false;
	}
};
