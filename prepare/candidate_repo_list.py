import requests
import random
import time
import sys
sys.path.append('/home/zhangyu/pawQL/')  #导入文件夹的.py文件
from prepare import init
from utils import file_opt
from prepare import queries
import matplotlib.pyplot as plt

max_star = 5000000

def read_token():
    token_file = open("../data/token_list.txt", 'r')
    tokens = token_file.readlines()
    return tokens

def query_request(query, last_star=None):
    tokens = read_token()
    token = tokens[random.randint(0,7)].strip()
    headers = {"Authorization": "Bearer %s" % token}
    if last_star:
        query_ = query % (last_star)
    else:
        query_ = query % (max_star)
    try:
        response = requests.post('https://api.github.com/graphql', json={'query': query_}, headers=headers, stream=True)
    except:
        print("request error and retry")
        time.sleep(1)
        r1 = query_request(query,last_star=last_star)
        return r1
    if response.status_code == 200:
        try:
            response.json()['data']
            return response.json()
        except Exception as e:
            print("token error or chunkedEncodingError")
            time.sleep(1)
            r1 = query_request(query,last_star=last_star)
            return r1
    else:
        print( str(response.status_code) + " retry")
        time.sleep(1)
        r1 = query_request(query,last_star=last_star)
        return r1


def search_repos():
    """
    获取满足search条件的repos list
    """
    output_response_file = init.local_data_filepath+"/candidate_repos_info.json"
    r = query_request(queries.search_candidate_repos)
    while r['data']['search']['nodes'][-1]['stargazerCount'] > 10000:
        last_star = r['data']['search']['nodes'][-1]['stargazerCount']
        r2 = query_request(queries.search_candidate_repos,last_star=last_star)
        r['data']['search']['nodes'] += r2['data']['search']['nodes'][1:]
        print("has finished ",len(r['data']['search']['nodes']))
    file_opt.save_json_to_file(output_response_file, r)

def create_initial_info():
    repos_info_file = init.local_data_filepath+"/candidate_repos_info.json"
    repo_info = file_opt.read_json_from_file(repos_info_file)
    repo_info_dict = []
    for item in repo_info['data']['search']['nodes']:
        languageKind = []
        for lang in item['languages']['nodes']:
            languageKind.append( lang['name'] )
        repo_info_dict.append({"owner":item['owner']['login'],"name":item['name'],"description":item['description'],
                               "forks":item['forkCount'],"stars":item['stargazerCount'],"languagesCount":item['languages']['totalCount'],
                               "languageKind":languageKind,"issues":item['issues']['totalCount'],"pullRequests":item['pullRequests']['totalCount']})
    return repo_info_dict

def remove_no_language(info_list):
    new_list = []
    for item in info_list:
        if item['languagesCount'] != 0:
            new_list.append(item)
    return new_list

def select_iss_pr_number(info_list):
    new_list = []
    issue_number , pr_number = [], []
    for item in info_list:
        issue_number.append(item['issues'])
        pr_number.append(item['pullRequests'])
        if item['issues'] > 500 and item['pullRequests'] > 500:
            new_list.append(item)
    # 查看issues和pr数的分布
    # issue_number = sorted(issue_number)
    # plt.hist(issue_number,bins=30,color='cornflowerblue')
    # plt.title("issue number ")
    # plt.show()
    #
    # pr_number = sorted(pr_number)
    # plt.hist(pr_number,bins=30,color='cornflowerblue')
    # plt.title("pr number ")
    # plt.show()
    #
    # print(issue_number)
    # print(pr_number)

    return new_list

def involve_common_language(info_list):
    common_language = ["C","Python","Java","C++","C#","Visual Basic","JavaScript","PHP","R","SQL"]
    new_list = []
    for item in info_list:
        for lang in common_language:
            if lang in item['languageKind']:
                new_list.append(item)
                break
    return new_list

def create_repo_list(repo_info):
    repo_list = []
    for item in repo_info:
        repo_list.append(item['owner']+"/"+item['name']+"\n")
    f = open("../data/repository_list_601.txt",'w')
    for item in sorted(repo_list):
        f.write(item)
    f.close()

def select_repos():
    initial_info_list = create_initial_info()
    clear_language_list = remove_no_language(initial_info_list)
    common_language_list = involve_common_language(clear_language_list)
    iss_pr_number_list = select_iss_pr_number(common_language_list)
    # 保存文件
    file_opt.save_json_to_file(init.local_data_filepath+"/after_select_respos.json",iss_pr_number_list)
    # 创建仓库列表
    create_repo_list(iss_pr_number_list)

if __name__ == '__main__':
    search_repos()        # 获取仓库的信息，一次获取之后就存储了文件，不需要每次都跑
    # select_repos()          # 按照条件筛选符合的仓库，并写下详细信息，以及生成repository_list.txt