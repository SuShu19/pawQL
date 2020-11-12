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

def query_request(query, owner, repo, type, last_end_cursor=None, number=None):
    tokens = read_token()
    token = tokens[random.randint(0,4)].strip()
    headers = {"Authorization": "Bearer %s" % token}
    if last_end_cursor:
        query_ = query % (owner, repo, type,last_end_cursor)
    elif number:
        query_ = query % (owner, repo, type, number)
    else:
        query_ = query % (owner, repo, type)

    try:
        response = requests.post(
            'https://api.github.com/graphql', json={'query': query_}, headers=headers, stream=True)
    except:
        print("request error and retry")
        time.sleep(1)
        r1 = query_request(query, owner, repo, type, last_end_cursor, number)
        return r1

    if response.status_code == 200:
        try:
            response.json()['data']
        except KeyError:
            r1 = query_request(query, owner, repo, type, last_end_cursor, number)
            return r1
        try:
            return response.json()
        except:
            print("return error and retry")
            time.sleep(1)
            r1 = query_request(query, owner, repo, type, last_end_cursor, number)
            return r1
    else:
        print( str(response.status_code) + " retry")
        time.sleep(1)
        r1 = query_request(query, owner, repo, type, last_end_cursor, number)
        return r1



def request_graphQL(owner, repo):
    """
    通过graphQL获取owner/repo仓库的pr和issue数据
    :param owner: repository owner
    :param repo:  repository name
    :param type:  pullRequests or issues
    :return:  response of pr and issues
    """
    types = ["pullRequests","issues"]
    # types = ["issues","pullRequests"]
    for type in types:
        count = 0
        if type == "pullRequests":
            first_page = queries.first_pr_page
            other_page = queries.other_pr_page
        elif type == "issues":
            first_page = queries.first_iss_page
            other_page = queries.other_iss_page
        output_response_file = init.local_data_filepath+owner+"/"+repo+"/response_"+type+".json"
        if os.path.isfile(output_response_file):
            r = file_opt.read_json_from_file(output_response_file)
        else:
            r = query_request(first_page, owner, repo, type)
        if not r['data']['repository'][type]['pageInfo']['hasNextPage']:
            continue
        while True:
            count += 1
            print(count,datetime.now(),r['data']['repository'][type]['totalCount'],len(r['data']['repository'][type]['nodes']))
            if count % 1 == 0:
                file_opt.save_json_to_file(output_response_file, r)
            else:
                pass
            earliest_pr_cursor = r['data']['repository'][type]['edges'][-1]['cursor']
            r2 = query_request(other_page, owner, repo, type, last_end_cursor=earliest_pr_cursor)
            r['data']['repository'][type]['pageInfo'] = r2['data']['repository'][type]['pageInfo']
            r['data']['repository'][type]['edges']+= r2['data']['repository'][type]['edges']
            r['data']['repository'][type]['nodes'] += r2['data']['repository'][type]['nodes']
            if not r['data']['repository'][type]['pageInfo']['hasNextPage']:
                file_opt.save_json_to_file(output_response_file, r)
                break

if __name__ == '__main__':
    for o_r in init.repos_to_get_info:
        owner, repo = o_r[0], o_r[1]
        request_graphQL(owner, repo)