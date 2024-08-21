document.addEventListener("DOMContentLoaded", function() {
    // 모든 폼 필드를 선택
    var pTags = document.querySelectorAll("#register-form p");
    pTags.forEach(function(p) {
        p.classList.add("form-group"); // 각 p 태그에 클래스 추가
    });
});