# proj_sql_mapping/__init__.py

import mysql.connector

'''
#######################################################
# CONNECTION 정보 함수
# 작성일 : 2024.06.20
####################################################### '''
def fn_connector(request):
    sub_conn = mysql.connector.connect(
        host="modamtech.com",
        port=3306,
        user="aeit",
        password="susx2020",
        database="aeit",
    )
    return sub_conn

def create_connection(request):
    """데이터베이스 연결 생성 및 반환."""
    try:
        conn = fn_connector(request)
        cursor = conn.cursor()
        current_username = request.user.username
        return conn, cursor, current_username
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return None, None, None

def close_connection(conn, cursor):
    """변경 사항을 커밋하고 연결 및 커서를 닫음."""
    if conn:
        conn.commit()
        cursor.close()
        conn.close()

def handle_sql_error(e, sql_name):
    """SQL 오류를 처리하고 적절하게 로그를 남김."""
    print(f"{sql_name} 실행 실패: ", e)
    return 9

# 이제 sql_mapping.py 및 sql_mapping_article.py에서 데이터베이스 연결 설정과
# 해제 코드를 반복하지 않고 이 함수들을 가져와 사용할 수 있습니다:
# from proj_sql_mapping import create_connection, close_connection, handle_sql_error
