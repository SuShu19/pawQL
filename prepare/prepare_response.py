import os
import requests
import random
import time
import sys
sys.path.append('/home/zhangyu/pawQL/')  #导入文件夹的.py文件
import init
from utils import file_opt
from prepare import queries
from datetime import datetime

def read_token():
    token_file = open("../data/token_list.txt", 'r')
    tokens = token_file.readlines()
    return tokens

def query_request(query, owner, repo, type, last_typenode=None, last_comennt=None, last_timelinItems=None,number=None,):
    tokens = read_token()
    token = tokens[random.randint(0,12)].strip()
    headers = {"Authorization": "Bearer %s" % token}
    if last_typenode:
        query_ = query % (owner, repo, type,',after:"'+last_typenode+'"')        # 获取100条以后的node,query=search_100_nodes
    elif last_comennt and number:
        query_ = query % (owner, repo, type[:-1], number, ',after:"'+last_comennt+'"')        # 获取100条以后的comment,query=search_morethan_100_comments
    elif last_timelinItems and number:
        query_ = query % (owner, repo, type[:-1], number, ',after:"'+last_timelinItems+'"')        # 获取100条以后的timelineItems,query=search_morethan_100_timelineItems
    elif number and last_comennt is None and last_timelinItems is None:
        query_ = query % (owner, repo, type, number)                        # 查询每一条crossReference,与查询100条以后的comment和timelineItems区别, query=search_one_node
    else:
        query_ = query % (owner, repo, type,'')       # 获取第一个100条nodes
    try:
        response = requests.post('https://api.github.com/graphql', json={'query': query_}, headers=headers, stream=True)
    except:
        print("request error and retry")
        time.sleep(1)
        r1 = query_request(query, owner, repo, type, last_typenode,last_comennt,last_timelinItems,number)
        return r1
    if response.status_code == 200:
        try:
            response.json()['data']
            return response.json()
        except Exception as e:
            print("token error or chunkedEncodingError")
            time.sleep(1)
            r1 = query_request(query, owner, repo, type, last_typenode,last_comennt,last_timelinItems,number)
            return r1
    else:
        print( str(response.status_code) + " retry")
        time.sleep(1)
        r1 = query_request(query, owner, repo, type, last_typenode,last_comennt,last_timelinItems,number)
        return r1

def request_morethan_100_nodes(re,owner, repo, type):
    check_locations = ['comments','timelineItems']
    search_query = [queries.sear_morethan_100_comments,queries.sear_morethan_100_timelineItems]
    for node in re['data']['repository'][type]['nodes']:
        for check_loca,query in zip(check_locations,search_query):
            while node[check_loca]['pageInfo']['hasNextPage'] == True:
                current_number = node['number']
                last_cursor = node[check_loca]['edges'][-1]['cursor']
                if check_loca == "comments":
                    r_ = query_request(query, owner, repo, type, last_comennt=last_cursor,number=current_number)
                elif check_loca == "timelineItems":
                    r_ = query_request(query, owner, repo, type, last_timelinItems=last_cursor, number=current_number)
                node[check_loca]['nodes'] += r_['data']['repository'][type[:-1]][check_loca]['nodes']
                node[check_loca]['edges'] += r_['data']['repository'][type[:-1]][check_loca]['edges']
                node[check_loca]['pageInfo']['hasNextPage'] = r_['data']['repository'][type[:-1]][check_loca]['pageInfo']['hasNextPage']
    return re

def request_graphQL(fullname_repo):
    """
    通过graphQL获取owner/repo仓库的pr和issue数据
    """
    owner = fullname_repo[0]
    repo = fullname_repo[1]
    types = ["pullRequests","issues"]
    # types = ["issues","pullRequests"]
    for type in types:
        count = 0
        # if type == "pullRequests":
        #     first_page = queries.first_pr_page
        #     other_page = queries.other_pr_page
        # elif type == "issues":
        #     first_page = queries.first_iss_page
        #     other_page = queries.other_iss_page
        output_response_file = init.local_data_filepath+owner+"/"+repo+"/response_"+type+".json"
        if os.path.isfile(output_response_file):
            r = file_opt.read_json_from_file(output_response_file)
        else:
            r = query_request(queries.search_100_nodes, owner, repo, type)
        if not r['data']['repository'][type]['pageInfo']['hasNextPage']:
            continue
        while True:
            count += 1
            print(owner+"/"+repo,count,datetime.now(),r['data']['repository'][type]['totalCount'],len(r['data']['repository'][type]['nodes']))
            if count % 1 == 0:
                file_opt.save_json_to_file(output_response_file, r)
            else:
                pass
            earliest_pr_cursor = r['data']['repository'][type]['edges'][-1]['cursor']
            r2 = query_request(queries.search_100_nodes, owner, repo, type, last_typenode=earliest_pr_cursor)
            r2 = request_morethan_100_nodes(r2, owner, repo, type)
            r['data']['repository'][type]['pageInfo'] = r2['data']['repository'][type]['pageInfo']
            r['data']['repository'][type]['edges']+= r2['data']['repository'][type]['edges']
            r['data']['repository'][type]['nodes'] += r2['data']['repository'][type]['nodes']
            if not r['data']['repository'][type]['pageInfo']['hasNextPage']:
                file_opt.save_json_to_file(output_response_file, r)
                break

if __name__ == '__main__':
    from concurrent.futures import ThreadPoolExecutor as PoolExecutor
    repolist = init.repos_to_get_info
    with PoolExecutor(max_workers=4) as executor:
        for _ in executor.map(request_graphQL, repolist):
            pass