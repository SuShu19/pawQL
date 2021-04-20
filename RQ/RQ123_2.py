"""
清楚掉self link
"""


import sys
sys.path.append('/home/zhangyu/pawQL/')  #导入文件夹的.py文件
import re
from datetime import datetime
from prepare import init
from utils import file_opt
from utils import visualization as vis
from prepare import prepare_response
from prepare import queries
from tqdm import tqdm
from prepare import preprocess
import os

def delete_self_loop(type_list_sl, filepath=None):
    type_list = []
    for item in type_list_sl:
        if not int(item['source']['number']) == int(item['target']['number']):
            type_list.append(item)
    file_opt.save_json_to_file(filepath + "links_type.json", type_list)
    return

def work(fullname_repo):
    owner, repo = fullname_repo[0], fullname_repo[1]
    print("--------------------handle " + owner + "/" + repo + "---------------------------")
    type_list_sl = file_opt.read_json_from_file(init.local_data_filepath+owner+"/"+repo+"/links_type_sl.json")
    delete_self_loop(type_list_sl, init.local_data_filepath + owner + "/" + repo + "/")    # 主程序
    print("--------------------finish " + owner + "/" + repo + "---------------------------")
    return

if __name__ == '__main__':
    from concurrent.futures import ThreadPoolExecutor as PoolExecutor
    repolist = init.repos_to_get_info
    with PoolExecutor(max_workers=5) as executor:
        for _ in executor.map(work, repolist):
            pass