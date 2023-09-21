const chat_container = document.querySelector('.chatbot-container');
const chat_circle = document.getElementById('chat-circle');
const inputForm = document.getElementById('input-form');
const inputField = document.getElementById('input-field');
const conversation = document.getElementById('conversation');

// 챗봇 토글 버튼 클릭 이벤트
chat_circle.addEventListener('click', function () {
    chat_container.style.display = 'block';
    chat_circle.style.display = 'none';
});

// 사용자 입력을 서버로 전송하고 챗봇 응답을 받아오는 함수
function generateResponse(input) {
    return fetch('http://oreumi-dangun.cyxsnajbfbeu.ap-northeast-2.rds.amazonaws.com/chatbot_response/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: input })
    })
        .then(response => response.json())
        .then(data => data.response)
        .catch(error => {
            console.error(error);
            return '챗봇이 응답하지 못했습니다.';
        });
}

// 입력 폼 제출 이벤트
inputForm.addEventListener('submit', function (event) {
    event.preventDefault();

    const input = inputField.value;

    inputField.value = '';
    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: "2-digit" });

    // 사용자 메시지를 대화창에 추가
    const userMessage = document.createElement('div');
    userMessage.classList.add('chatbot-message', 'user-message');
    userMessage.innerHTML = `<p class="chatbot-text" sentTime="${currentTime}">${input}</p>`;
    conversation.appendChild(userMessage);

    // 챗봇 응답을 생성하고 대화창에 추가
    generateResponse(input)
        .then(response => {
            const botMessage = document.createElement('div');
            botMessage.classList.add('chatbot-message', 'chatbot');
            botMessage.innerHTML = `<p class="chatbot-text" sentTime="${currentTime}">${response}</p>`;
            conversation.appendChild(botMessage);
            botMessage.scrollIntoView({ behavior: "smooth" });
        })
        .catch(error => {
            console.error(error);
        });
});