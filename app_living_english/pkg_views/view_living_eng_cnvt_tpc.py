from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from proj_sql_mapping import mdl_proj_sql_mapping as sql_statement


@login_required(login_url='/login/')
def main_cnvrt_tpc_exec(request):

    existing_topic = sql_statement.sql_dao(request, "sqls_proj_converted_sentn", "main_cnvrt_tpc_exec")

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

    return render(request, "living_english_cnvt_tpc.html", value)

