document.addEventListener("DOMContentLoaded", function () {
    const chatContainer = document.querySelector(".chat-container");
    const chatInput = document.querySelector(".chat-input textarea");
    const submitButton = document.querySelector(".chat-input button");

    // 챗봇 메시지를 채팅 컨테이너에 추가하는 함수
    function addMessage(message, isBot) {
        const messageBox = document.createElement("div");
        messageBox.className = isBot ? "message-box from-bot" : "message-box from-user";
        messageBox.innerHTML = `
        <div class="message-text">${message}</div>
        <p class="s-text">${getCurrentTime()}</p>
      `;
        chatContainer.appendChild(messageBox);

        // 챗 컨테이너의 하단으로 스크롤
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // 현재 시간을 가져오는 함수 (이 부분을 필요에 따라 변경할 수 있습니다)
    function getCurrentTime() {
        const now = new Date();
        const hours = now.getHours();
        const minutes = now.getMinutes();
        return `${hours}:${minutes}`;
    }

    // 사용자 입력을 처리하는 함수
    function handleUserInput() {
        const userMessage = chatInput.value;
        addMessage(userMessage, false);

        // 사용자 메시지를 서버로 보내고 (이 부분을 구현해야 합니다)
        // 서버로부터 응답을 받거나 응답을 시뮬레이트합니다
        const botResponse = "안녕하세요, 저는 챗봇입니다! 어떻게 도와드릴까요?";
        setTimeout(function () {
            addMessage(botResponse, true);
        }, 1000); // 챗봇 응답을 시뮬레이트하기 위한 지연 시간 (조정 가능)

        // 입력 필드를 지우기
        chatInput.value = "";
    }

    // 채팅 입력 양식 제출을 처리하는 이벤트 리스너
    submitButton.addEventListener("click", function (event) {
        event.preventDefault();
        handleUserInput();
    });
});