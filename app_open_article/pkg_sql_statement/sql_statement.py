import re

import spacy

from app_common import mdl_common_app as comn_func
from app_news_study.pkg_mdl_common import mdl_common_news as app_comn_func
from app_news_study.pkg_sql_statement import create_connection, close_connection, handle_sql_error

'''
#######################################################
# CONNECTION 정보 함수
# 작성일 : 2024.06.20
####################################################### '''
def sql_dao(request, sql_name, p_param):
    conn, cursor, current_username = create_connection(request)

    try:
        ''' 
        ##############
         SELECT BLOCK
        ##############  '''
        ''' 
        ##############
         INSERT BLOCK
        ############## '''
        ''' 
        ##############
         UPDATE BLOCK
        ############## '''

    except Exception as e:
        return handle_sql_error(e, sql_name)

    finally:
        close_connection(conn, cursor)