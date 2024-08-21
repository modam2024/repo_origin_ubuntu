    $(document).ready(function() {
        function splitCnvtText(text) {
            var cnvt_text = ""
            var cnvt_text_arr = text.split(":");  // 텍스트 영역의 값을 가져옵니다.

            if (cnvt_text_arr.length > 1){
                cnvt_text = cnvt_text_arr[1].trim();
            } else {
                cnvt_text = cnvt_text_arr[0].trim();
            }
            return cnvt_text;
        }
        function splitCnvtAllText(text) {
            var tmp_text = text.replace(/undefined/g, "");
            var cnvt_text_arr = tmp_text.split("A :");  // 텍스트 영역의 값을 가져옵니다.

            var second_text = ""
            for (var each_text_A of cnvt_text_arr)
            {
                var cnvt_text_B_arr = each_text_A.trim().split("B :");
                for (var each_text_B of cnvt_text_B_arr) {
                    second_text += "\n" + each_text_B.trim();
                }
            }

            return second_text
        }
     });