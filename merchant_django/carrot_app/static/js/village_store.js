document.addEventListener("DOMContentLoaded", () => {
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

    // 카테고리를 자동으로 선택하고 가게 정보를 검색하는 함수
    function loadInitialCategory() {
        const categoryCodes = ['FD6', 'CE7', 'AG2'];
        const randomCategoryCode = categoryCodes[Math.floor(Math.random() * categoryCodes.length)];
        searchPlaces(randomCategoryCode, 37.566826, 126.9786567);
    }

    // 사용자의 현재 위치를 얻어오고 가게 정보를 검색하는 함수
    function searchPlaces(categoryCode, userLat, userLng) {
        // API 요청 헤더에 인증정보 추가
        const headers = {
            'Authorization': 'KakaoAK c288569d698f5dfcbb3b254fdf2f7b31'
        };

        // 카테고리에 해당하는 가게 정보 불러오기 (jQuery AJAX 사용)
        $.ajax({
            url: `https://dapi.kakao.com/v2/local/search/category.json?category_group_code=${categoryCode}&x=${userLng}&y=${userLat}&radius=1000&page=1&size=8&sort=accuracy`,
            type: 'GET',
            headers: headers,
            setTimeout: 300000,
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
    }

    // 페이지 로드 시 초기 카테고리 불러오기
    loadInitialCategory();


    // 전체 카테고리에 active 클래스 추가 (페이지 로드시)
    $('.menu_label:contains("전체")').addClass('active');

    // 각 카테고리를 클릭했을 때 (jQuery 이벤트 핸들러 사용)
    menu1.on('click', 'input[type="radio"]', (event) => {
        const category = $(event.target).parent().text().trim(); // 선택한 카테고리 텍스트
        let categoryCode;

        // 기존에 활성화된 카테고리의 active 클래스를 제거
        $('.menu_label').removeClass('active');

        if (category === '전체') {
            const categoryCodes = ['FD6', 'CE7', 'AG2'];
            categoryCode = categoryCodes[Math.floor(Math.random() * categoryCodes.length)];
        } else if (category === '식당') {
            categoryCode = 'FD6';
        } else if (category === '카페') {
            categoryCode = 'CE7';
        } else if (category === '부동산') {
            categoryCode = 'AG2';
        } else if (category === '마트') {
            categoryCode = 'MT1';
        } else if (category === '편의점') {
            categoryCode = 'CS2';
        }

        // 선택한 카테고리에 active 클래스 추가
        $(event.target).parent().addClass('active');

        // 사용자의 현재 위치를 얻어오고 가게 정보를 검색
        navigator.geolocation.getCurrentPosition(function (position) {
            const userLat = position.coords.latitude;
            const userLng = position.coords.longitude;

            // 가게 정보 검색 함수 호출
            searchPlaces(categoryCode, userLat, userLng);
        });
    });

    // 가게 정보를 menu2에 표시하는 함수
    function displayPlaces(data) {
        menu2.empty(); // 이전 정보 초기화

        data.forEach(place => {
            // 가게 정보를 표시할 각 요소 생성
            const listItem = `
            <a href="${place.place_url}" target="_blank" style="display: flex; align-items: center; padding: 10px;">
        <div style="margin-right: 10px;">
        <img src="/static/img/kakao.png" alt="이미지" style="width: 100px; height: 100px;">
        </div>
        <div style="display: flex; flex-direction: column; ">
            <div style="margin-bottom: 5px;">
                <span style="color: black; display: block; font-weight: 600; font-size:20px;">${place.place_name}</span>
            </div>
            <div style="margin-bottom: 5px;font-size:20px;">
                <span style="color: black; display: block;">${place.address_name}</span>
            </div>
            <div style="margin-bottom: 5px;font-size:20px;">
                <span style="color: black; display: block;">${place.phone}</span>
            </div>
            <span style="color: black; display: block;  ">${place.category_name}</span>
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
                <img src="static/img/kakao.png" alt="이미지"
                style="width: 100px; height: 100px;">
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