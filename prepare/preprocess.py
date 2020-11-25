import re
def clear_body(body):
    # 删除引用
    body = re.compile(r'>.*\n').sub("",body)

    # 删除段落代码段
    body = re.compile(r'```[\s\S]*```').sub("",body)

    # 删除行内代码
    body = re.compile(r'`[\s\S]*`').sub("",body)

    return body
