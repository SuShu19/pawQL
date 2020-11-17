import re

def replace_pattern(patter_list,body):
    if patter_list:
        for i in range(0, len(patter_list)):
            body = body.replace(patter_list[i], '')
    return body

def clear_body(body):
    # 删除引用
    quote = re.findall(re.compile(r'>.*\n'), body)
    body = replace_pattern(quote,body)

    # 先删除段落代码段
    code_segment = re.findall(re.compile(r'```[\s\S]*```'), body)
    body = replace_pattern(code_segment,body)

    # 后删除行内代码
    code_segment_in_line = re.findall(re.compile(r'`[\s\S]*`'), body)
    body = replace_pattern(code_segment_in_line,body)

    return body
