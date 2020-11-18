import re
# todo 预处理的结果错了，要重新再跑一遍，哭...
def clear_body(body):
    # 删除引用
    body = re.compile(r'>.*\n').sub("",body)

    # 删除段落代码段
    body = re.compile(r'```[\s\S]*```').sub("",body)

    # 删除行内代码
    body = re.compile(r'`[\s\S]*`').sub("",body)

    return body
