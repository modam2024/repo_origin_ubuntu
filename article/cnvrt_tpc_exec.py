from django.shortcuts import render
from mdl_sql_mapping import sql_mapping as sql_statement
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
def main_cnvrt_tpc_exec(request):

    existing_topic = sql_statement.sql_dao(request, "sqls_select_tb_converted_sentn", "main_cnvrt_tpc_exec")

    rows = []

    for record in existing_topic:
        (
            no,
            topic_num,
            src_title,
            whitespace_converted,
            converted_sentn,
            original_sentn
        ) = record

        rows.append((no, topic_num, src_title, whitespace_converted, converted_sentn, original_sentn))

    value = {
        "sent_rows":  rows,
    }

    return render(request, "cnvt_tpc_exec.html", value)

