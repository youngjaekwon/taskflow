let message = $state('');

export const announcer = {
	get message() {
		return message;
	},

	announce(text: string) {
		// 동일 메시지를 연속으로 보내도 스크린 리더가 감지하도록 초기화 후 설정
		message = '';
		requestAnimationFrame(() => {
			message = text;
		});
	}
};
