document.addEventListener("DOMContentLoaded", () => {
    // Kakao Maps API 로드 완료되면 실행
    // 카카오 맵 API 로드 완료 후 실행
    kakao.maps.load(() => {
        const places = new kakao.maps.services.Places();
        const menu1 = $('.menu1'); // jQuery를 이용하여 요소 선택
        const menu2 = $('.menu2'); // jQuery를 이용하여 요소 선택
        let map;  // 여기에 지도 객체를 저장할 변수를 선언

        // 지도를 생성하고 변수에 저장
        const mapContainer = document.getElementById('map');
        const mapOption = {
            center: new kakao.maps.LatLng(37.566826, 126.9786567), // 지도의 중심좌표
            level: 5 // 지도의 확대 레벨
        };
        map = new kakao.maps.Map(mapContainer, mapOption);

        // 각 카테고리를 클릭했을 때 (jQuery 이벤트 핸들러 사용)
        menu1.on('click', 'input[type="radio"]', (event) => {
            const category = $(event.target).parent().text().trim(); // 선택한 카테고리 텍스트

            // API 요청 헤더에 인증정보 추가
            const headers = {
                'Authorization': 'KakaoAK c288569d698f5dfcbb3b254fdf2f7b31'
            };

            // 카테고리에 해당하는 가게 정보 불러오기 (jQuery AJAX 사용)
            $.ajax({
                url: `https://dapi.kakao.com/v2/local/search/category.json?category_group_code=80&query=${category}`,
                type: 'GET',
                headers: headers,
                success: function (data, status) {
                    if (status === 'success') {
                        // 가게 정보를 menu2에 표시
                        displayPlaces(data.documents);
                    } else {
                        console.error('가게 정보를 불러오지 못했습니다.');
                    }
                },
                error: function (xhr, status, error) {
                    console.error('가게 정보를 불러오지 못했습니다.', error);
                }
            });
        });

        // 가게 정보를 menu2에 표시하는 함수
        function displayPlaces(data) {
            menu2.empty(); // 이전 정보 초기화

            data.forEach(place => {
                // 가게 정보를 표시할 각 요소 생성
                const listItem = `
                    <a href="${place.place_url}" target="_blank">
                        <div>
                            <div>
                                <img src="${place.place_url}" alt="${place.place_name} 이미지">
                            </div>
                        </div>
                        <div>
                            <div>
                                <span>${place.place_name}</span>
                                <span>${place.address_name}</span>
                            </div>
                            <span>${place.phone}</span>
                            <span>${place.category_name}</span>
                        </div>
                    </a>
                `;

                // 각 가게를 클릭했을 때 상세 정보 표시
                const listItemElement = $(listItem);
                listItemElement.on('click', () => {
                    // 모달 창 열기
                    const modal = $('#modal');
                    modal.css('display', 'block');

                    // 선택한 가게의 정보를 모달에 표시
                    const modalContent = $('#modal-content');
                    modalContent.html(`
                        <h2>${place.place_name}</h2>
                        <p>주소: ${place.address_name}</p>
                        <p>전화번호: ${place.phone}</p>
                        <p>카테고리: ${place.category_name}</p>
                        <!-- 기타 가게 정보를 추가하세요 -->
                    `);
                });

                menu2.append(listItemElement); // menu2에 추가
            });
        }
    });
});
