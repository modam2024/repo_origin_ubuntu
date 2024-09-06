# 장고 서버가 죽었을 때 다시 시작하기 위한 shell 파일이다.

if ! curl -s http://119.205.220.168:8000 > /dev/null; then
    echo "서버가 응답하지 않음, 서버 재시작..."

    source venv/bin/activate  # 가상 환경 활성화, 필요한 경우
    ~/start_django.sh
else
    echo "서버가 정상적으로 실행 중임."
fi

