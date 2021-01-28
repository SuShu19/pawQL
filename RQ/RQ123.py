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

renew = 1       # 0-直接读文件，1-续写文件，2-重写文件 todo 把2写完

def parse_node2(url):
    item = url.split("/")
    type = item[-2]
    if type == "pull":  # 统一type的名字为 pullRequests 和 issues
        type = "pullRequest"
    elif type == "issues":
        type = "issue"
        pass
    number = item[-1]
    owner = item[-4]
    name = item[-3]
    return url, owner, name, type, number

def determine_link_type(node1_type, node2_type):
    if node1_type == "pullRequest" and node2_type == 'pullRequest':
        link_type = "pullRequest to pullRequest"
    if node1_type == "issue" and node2_type == 'pullRequest':
        link_type = "issue to pullRequest"
    if node1_type == "pullRequest" and node2_type == 'issue':
        link_type = "pullRequest to issue"
    if node1_type == "issue" and node2_type == 'issue':
        link_type = "issue to issue"
    return link_type

def parse_node2_in_url(nodes, url, location, node1,link_time, pr_list, pr_createAt, issue_list, issue_createAt,owner, name):
    node2_url, node2_owner, node2_name, node2_type, node2_number = parse_node2(url)
    if node2_owner != owner and node2_name != name:
        print(node2_url+" is crossRepository.")
        return None
    if node2_type != "pullRequest" and node2_type != "issue":
        return None
    else:
        pass
    if node2_type == "pullRequest":
        try:
            node2_time = pr_createAt[pr_list.index(int(node2_number))]
        except ValueError:
            try:
                node2_time = pr_createAt[issue_list.index(int(node2_number))]
                node2_type = "issue"
                node2_url = node2_url.replace("pull","issues")
            except ValueError:
                print(node2_url+" does not exist in this repo.")
                return None

    elif node2_type == "issue":
        try:
            node2_time = issue_createAt[issue_list.index(int(node2_number))]
        except ValueError:
            try:
                node2_time = pr_createAt[pr_list.index(int(node2_number))]
                node2_type = "pullRequest"
                node2_url = node2_url.replace("issues", "pull")
            except ValueError:
                print(node2_url+" does not exist in this repo.")
                return None

    create_time_interval = datetime.strptime(node2_time, "%Y-%m-%dT%H:%M:%SZ") \
        .__sub__(datetime.strptime(node1['time'], "%Y-%m-%dT%H:%M:%SZ")).days

    link_time_interval = datetime.strptime(link_time, "%Y-%m-%dT%H:%M:%SZ") \
        .__sub__(datetime.strptime(node1['time'], "%Y-%m-%dT%H:%M:%SZ")).days

    link_type = determine_link_type(node1["type"], node2_type)
    if node1['url'].split("/")[:5] == node2_url.split("/")[:5]:
        isCrossRepository = False
    else:
        isCrossRepository = True

    # 找到node2信息，确定file list
    node2_files = 0
    node2_file_path = []
    for node2 in nodes:
        if node2["number"] == int(node2_number):
            if "changedFiles" in node2.keys():
                node2_files = node2["changedFiles"]
            node2_file_path = []
            if "files" in node2.keys():
                if node2["files"] is not None:
                    for path in node2["files"]["nodes"]:
                        node2_file_path.append(path["path"])
                    else:
                        pass
            break

    return {'source':{'number': node1['number'], 'url': node1['url'], 'createdAt':node1['time'],'files':node1["file_list"],'file_count':node1["file_count"]},
            'target':{'number': int(node2_number), 'url': node2_url,'createdAt':node2_time,'create_time_interval': create_time_interval,
                      "link_time_interval":link_time_interval,'type': link_type, 'location': location,
                      'isCrossRepository': isCrossRepository,'files':node2_file_path,'file_count':node2_files}}

def determine_number_type(pr_list, issue_list, number):
    if int(number) in pr_list:
        return "pullRequest"
    elif int(number) in issue_list:
        return "issue"
    else:
        return None

def parse_node2_in_num(nodes,quote_num, location, node1, owner, name, link_time, pr_list, pr_createAt, issue_list, issue_createAt,):
    global node2_file_path, node2_files
    node2_number = quote_num.replace("#", '')
    node2_type = determine_number_type(pr_list, issue_list, node2_number)
    if node2_type == None:
        return None
    if node2_type == "pullRequest":
        type_str = "pull"
        node2_time = pr_createAt[pr_list.index(int(node2_number))]
    elif node2_type == "issue":
        type_str = "issues"
        node2_time = issue_createAt[issue_list.index(int(node2_number))]
    node2_url = "https://github.com/" + owner + "/" + name + "/" + type_str +"/"+ node2_number
    create_time_interval = datetime.strptime(node2_time, "%Y-%m-%dT%H:%M:%SZ") \
        .__sub__(datetime.strptime(node1['time'], "%Y-%m-%dT%H:%M:%SZ")).days
    link_time_interval = datetime.strptime(link_time, "%Y-%m-%dT%H:%M:%SZ") \
        .__sub__(datetime.strptime(node1['time'], "%Y-%m-%dT%H:%M:%SZ")).days
    link_type = determine_link_type(node1["type"], node2_type)
    if node1['url'].split("/")[:5] == node2_url.split("/")[:5]:
        isCrossRepository = False
    else:
        isCrossRepository = True
    # 找到node2信息，确定file list
    node2_files = 0
    node2_file_path = []
    for node2 in nodes:
        if node2["number"] == int(node2_number):
            if "changedFiles" in node2.keys():
                node2_files = node2["changedFiles"]
            node2_file_path = []
            if "files" in node2.keys():
                if node2["files"] is not None:
                    for path in node2["files"]["nodes"]:
                        node2_file_path.append(path["path"])
                else:
                    pass
            break
    return {'source':{'number': node1['number'], 'url': node1['url'], 'createdAt':node1['time'],'files':node1["file_list"],'file_count':node1["file_count"]},
            'target':{'number': int(node2_number), 'url': node2_url,'createdAt':node2_time, 'create_time_interval':create_time_interval,
                      'link_time_interval': link_time_interval,'type': link_type, 'location': location,
                      'isCrossRepository': isCrossRepository,'files':node2_file_path,'file_count':node2_files}}

def detect_dup(links,link):
    repeat = 0
    for i in range(len(links)-1, -1, -1):
        if int(link['source']['number']) == int(links[i]['source']['number']) and \
                int(link['target']['number']) == int(links[i]['target']['number']):
            repeat = 1
            # 比较两个link的link time interval, 取小的那一个，是更早的一条link
            if link['target']['link_time_interval'] < links[i]['target']['link_time_interval']:
                links[i]['target']['link_time_interval'] = link['target']['link_time_interval']
                links[i]['target']['create_time_interval'] = link['target']['create_time_interval']
                links[i]['target']['location'] = link['target']['location']
            else:
                pass
        else:
            pass
    if repeat == 0:
        links.append(link)
    return links

def extract_link_in_title(nodes, node, links):
    title_quote = re.findall(re.compile(r'#[0-9]+'), node['title'])
    if len(title_quote) != 0:
        for quote in title_quote:
            source_number = node['number']
            target_number = quote.replace("#",'')
            for target_node in nodes:
                if target_node['number'] == int(target_number):
                    source_url = node['url']
                    target_url = target_node['url']
                    source_file = get_file(node)
                    target_file = get_file(target_node)
                    create_time_interval = datetime.strptime(target_node['createdAt'], "%Y-%m-%dT%H:%M:%SZ").__sub__(
                        datetime.strptime(node['createdAt'], "%Y-%m-%dT%H:%M:%SZ")).total_seconds()
                    link_time_interval = 1  # title里的link都是在创建node的时候就link上了，所以这里定义link time interval为1秒
                    link_type = determine_link_type(extract_type_in_url(source_url), extract_type_in_url(target_url))
                    link = {'source': {'number': source_number, 'url': source_url, 'createdAt': node['createdAt'],
                               'files': source_file},
                            'target': {'number': target_number, 'url': target_url, 'createdAt': target_node['createdAt'],
                                       'create_time_interval': create_time_interval,'link_time_interval': link_time_interval,
                                       'type': link_type, 'location': "title",'files': target_file}}
                    links = detect_dup(links,link)
    return links

def extract_link_in_body(nodes, node, links):
    target_number_list = []
    body_url = []
    body_url += re.findall(re.compile(r'https://github.com/' + node['url'].split('/')[-4] + '/' + node['url'].split('/')[-3] + '/+pull+/+[0-9]+'), preprocess.clear_body(node['body']))
    body_url += re.findall(re.compile(r'https://github.com/' + node['url'].split('/')[-4] + '/' + node['url'].split('/')[-3] + '/+issues+/+[0-9]+'), preprocess.clear_body(node['body']))
    if len(body_url) != 0:
        for url in body_url:
            target_number_list.append(url.split('/')[-1])
    body_quote = re.findall(re.compile(r'#[0-9]+'), preprocess.clear_body(node['body']))
    if len(body_quote) != 0:
        for quote in body_quote:
            target_number_list.append(quote.replace("#",""))
    for target_number in target_number_list:
        for target_node in nodes:
            if target_node['number'] == int(target_number):
                source_number = node['number']
                source_url = node['url']
                target_url = target_node['url']
                source_file = get_file(node)
                target_file = get_file(target_node)
                create_time_interval = datetime.strptime(target_node['createdAt'], "%Y-%m-%dT%H:%M:%SZ").__sub__(
                    datetime.strptime(node['createdAt'], "%Y-%m-%dT%H:%M:%SZ")).total_seconds()
                link_time_interval = 1  # title里的link都是在创建node的时候就link上了，所以这里定义link time interval为1秒
                link_type = determine_link_type(extract_type_in_url(source_url), extract_type_in_url(target_url))
                link = {'source': {'number': source_number, 'url': source_url, 'createdAt': node['createdAt'],
                                   'files': source_file},
                        'target': {'number': target_number, 'url': target_url, 'createdAt': target_node['createdAt'],
                                   'create_time_interval': create_time_interval,
                                   'link_time_interval': link_time_interval,
                                   'type': link_type, 'location': "body", 'files': target_file}}
                links = detect_dup(links, link)
    return links

def extract_link_in_comment(nodes, node, links):
    # 处理comment
    for comment in node['comments']['nodes']:
        target_number_list = []
        comment_url = []
        comment_url += re.findall(re.compile(r'https://github.com/' + node['url'].split('/')[-4] + '/' + node['url'].split('/')[-3] + '/+pull+/+[0-9]+'), preprocess.clear_body(comment['body']))
        comment_url += re.findall(re.compile(r'https://github.com/' + node['url'].split('/')[-4] + '/' + node['url'].split('/')[-3] + '/+issues+/+[0-9]+'), preprocess.clear_body(comment['body']))
        if len(comment_url) != 0:
            for url in comment_url:
                target_number_list.append(url.split('/')[-1])
        comment_quote = re.findall(re.compile(r'#[0-9]+'), preprocess.clear_body(comment['body']))
        if len(comment_quote) != 0:
            for quote in comment_quote:
                target_number_list.append(quote.replace("#",""))

        for target_number in target_number_list:
            for target_node in nodes:
                if target_node['number'] == int(target_number):
                    source_number = node['number']
                    source_url = node['url']
                    target_url = target_node['url']
                    source_file = get_file(node)
                    target_file = get_file(target_node)
                    create_time_interval = datetime.strptime(target_node['createdAt'], "%Y-%m-%dT%H:%M:%SZ").__sub__(
                        datetime.strptime(node['createdAt'], "%Y-%m-%dT%H:%M:%SZ")).total_seconds()
                    link_time_interval = datetime.strptime(comment['createdAt'], "%Y-%m-%dT%H:%M:%SZ").__sub__(
                        datetime.strptime(node['createdAt'], "%Y-%m-%dT%H:%M:%SZ")).total_seconds()
                    link_type = determine_link_type(extract_type_in_url(source_url), extract_type_in_url(target_url))
                    link = {'source': {'number': source_number, 'url': source_url, 'createdAt': node['createdAt'],
                                       'files': source_file},
                            'target': {'number': target_number, 'url': target_url, 'createdAt': target_node['createdAt'],
                                       'create_time_interval': create_time_interval,
                                       'link_time_interval': link_time_interval,
                                       'type': link_type, 'location': "comment", 'files': target_file}}
                    links = detect_dup(links, link)
    return links

def extract_link_in_review(node, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt, links):
    # 处理comment
    location = 'review'
    if len(node['reviews']['nodes']) != 0:
        for review in node['reviews']['nodes']:
            review_comments = review['comments']['nodes']
            for rc in review_comments:
                review_url = []
                review_url += re.findall(re.compile(r'https://github.com/' + owner + '/' + name + '/+pull+/+[0-9]+'), rc['body'])
                review_url += re.findall(re.compile(r'https://github.com/' + owner + '/' + name + '/+issues+/+[0-9]+'), rc['body'])
                if len(review_url) != 0:
                    location = 'review'
                    for url in review_url:
                        link = parse_node2_in_url(url, location, node1,pr_list, pr_createAt, issue_list, issue_createAt,owner,name)
                        links = detect_dup(links,link)
                # 处理body中的#12345的link
                comment_quote = re.findall(re.compile(r'#[0-9]+'), rc['body'])
                if len(comment_quote) != 0:
                    for quote in comment_quote:
                        link = parse_node2_in_num(quote, location, node1, owner, name, pr_list, issue_list)
                        links = detect_dup(links,link)
    return links

def get_file(unit):
    # 获取当前task unit修改的文件列表
    file_path = []
    if "changedFiles" in unit.keys():
        if unit["files"] is not None:
            for path in unit["files"]['nodes']:
                file_path.append(path["path"])
        else:
            pass
    else:
        pass
    return file_path

def extract_link_in_crossReference(nodes, node, links):
    # 处理crossReference, 从target找source
    for item in node['timelineItems']['nodes']:
        if item:
            if "source" not in item:                      # 排除ReferencedAt的情况
                continue
            source_number = item['source']['number']
            source_url = item['source']['url']
            target_number = item['target']['number']
            target_url = item['target']['url']
            create_time_interval = datetime.strptime(item['target']['createdAt'], "%Y-%m-%dT%H:%M:%SZ").__sub__(
                datetime.strptime(item['source']['createdAt'], "%Y-%m-%dT%H:%M:%SZ")).total_seconds()
            link_time_interval = datetime.strptime(item['referencedAt'], "%Y-%m-%dT%H:%M:%SZ").__sub__\
                (max(datetime.strptime(item['source']['createdAt'], "%Y-%m-%dT%H:%M:%SZ"),
                     datetime.strptime(item['target']['createdAt'], "%Y-%m-%dT%H:%M:%SZ"))).total_seconds()
            target_file_path = get_file(node)
            link_type = determine_link_type(extract_type_in_url(source_url), extract_type_in_url(target_url))
            # 找source
            for source_node in nodes:
                if source_node['number'] == source_number:
                    # 提取source file
                    source_file_path = get_file(source_node)
                    # 确定location ，这里只有body和comment两种情况，用正则匹配出来
                    # body
                    link_text = re.findall(re.compile(r'#+%s' % str(target_number)), preprocess.clear_body(source_node['body']))
                    if len(link_text) != 0:
                        location = "body"
                        link = {'source':{'number': source_number, 'url': source_url, 'createdAt': item['source']['createdAt'],
                                                'files':source_file_path},
                                      'target':{'number': target_number, 'url': target_url, 'createdAt':item['target']['createdAt'],
                                                'create_time_interval': create_time_interval,'link_time_interval':link_time_interval,
                                                'type': link_type, 'location': location, 'files':target_file_path}}
                        links = detect_dup(links,link)
                    # comment
                    for comment in source_node['comments']['nodes']: # todo 这里comment一条记录都没有，检查一下
                        link_text = re.findall(re.compile(r'#+%s' % str(target_number)), preprocess.clear_body(comment['body']))
                        if len(link_text) != 0:
                            location = "comment"
                            link = {'source':{'number': source_number, 'url': source_url, 'createdAt': item['source']['createdAt'],
                                                'files':source_file_path},
                                      'target':{'number': target_number, 'url': target_url, 'createdAt':item['target']['createdAt'],
                                                'create_time_interval': create_time_interval,'link_time_interval':link_time_interval,
                                                'type': link_type, 'location': location, 'files':target_file_path}}
                            links = detect_dup(links, link)
    return links

def fetch_ReferencedEvent_source(source_number, source_owner, source_name, source_type):
    r = prepare_response.query_request(queries.search_one_node, source_owner, source_name, type=source_type, number=source_number)
    if "errors" in r:
        return None
    response_one = {}
    if "pullRequest" in r['data']['repository']:
        response_one['source_type'] = "pullRequest"
    else:
        response_one['source_type'] = "issue"
    response_one['createdAt'] = r['data']['repository'][response_one['source_type']]['createdAt']
    response_one['url'] = r['data']['repository'][response_one['source_type']]['url']
    # 提取file
    if "changedFiles" in r['data']['repository'][response_one['source_type']].keys():
        target_files = r['data']['repository'][response_one['source_type']]["changedFiles"]
        target_file_path = []
        if r['data']['repository'][response_one['source_type']]["files"] is not None:
            for path in r['data']['repository'][response_one['source_type']]["files"]['nodes']:
                target_file_path.append(path["path"])
        else:
            pass
    else:
        target_files = 0
        target_file_path = []
    response_one['file_count'] = target_files
    response_one['file_path'] = target_file_path

    return response_one

def extract_link_in_referencedEvent(nodes, node, links):
    for item in node['timelineItems']['nodes']:
        if item:
            if "commitRepository" not in item:                      # 排除ReferencedAt的情况
                continue
            if item['commit'] is None:
                continue
            if item['isCrossRepository'] == True:
                continue
            target_number = item['subject']['url'].split("/")[-1]
            target_url = item['subject']['url']

            urls = []
            urls += re.findall(re.compile(r'https://github.com/+\S+/+\S+/+pull+/+[0-9]+'), item['commit']['messageHeadlineHTML'])
            urls += re.findall(re.compile(r'https://github.com/+\S+/+\S+/+issues+/+[0-9]+'), item['commit']['messageHeadlineHTML'])
            if urls == []:
                continue
            for match_url in urls:
                if match_url.replace(match_url.split('/')[-2],'') == item['subject']['url'].replace(item['subject']['url'].split('/')[-2],''):
                    continue
                else:
                    source_number = match_url.split('/')[-1]
                    for source_node in nodes:
                        if source_node['number'] == int(source_number):
                            create_time_interval = datetime.strptime(item['subject']['createdAt'],"%Y-%m-%dT%H:%M:%SZ").__sub__(
                                datetime.strptime(source_node['createdAt'], "%Y-%m-%dT%H:%M:%SZ")).total_seconds()
                            link_time_interval = datetime.strptime(item['createdAt'], "%Y-%m-%dT%H:%M:%SZ").__sub__ \
                                (max(datetime.strptime(item['subject']['createdAt'], "%Y-%m-%dT%H:%M:%SZ"),
                                     datetime.strptime(source_node['createdAt'], "%Y-%m-%dT%H:%M:%SZ"))).total_seconds()
                            source_url = source_node['url']
                            source_file = get_file(source_node)
                            target_file = get_file(node)
                            source_type = extract_type_in_url(source_url)
                            if source_type is not None:
                                link_type = determine_link_type(source_type, extract_type_in_url(target_url))
                            else:
                                continue
                            if link_type == None:
                                continue
                            link = {'source':{'number': source_number, 'url': source_url, 'createdAt': source_node['createdAt'],
                                                'files':source_file},
                                      'target':{'number': target_number, 'url': target_url, 'createdAt':item['subject']['createdAt'],
                                                'create_time_interval': create_time_interval,'link_time_interval':link_time_interval,
                                                'type': link_type, 'location': "commit", 'files':target_file}}
                            detect_dup(links,link)
    return links

def extract_type_in_url(url):
    mark = url.split("/")[-2]
    if mark == "pull":
        type_ = "pullRequest"
    elif mark == "issues":
        type_ = "issue"
    else:
        type_ = None
    return type_

def extract_link_type(response_p, response_i, renew, filepath=None):
    if renew == 1:
        nodes = response_p['data']['repository']['pullRequests']['nodes'] + response_i['data']['repository']['issues']['nodes']
        if os.path.isfile(filepath + "links_type.json"):        # 如果已有link_type.json，查找后断点重启
            links = file_opt.read_json_from_file(filepath + "links_type.json")
        else:                                                   # 从0开始提取Link
            links = []
        continue_nodes = []
        for node in nodes:          # 用来找到新的起点
            if links == []:
                continue_nodes = nodes
                break
            else:
                if str(node['number']) == str(links[-1]['source']['number']):
                    continue_nodes = nodes[nodes.index(node)+1:]
                    break
                else:
                    continue
        if continue_nodes != []:
            for node in tqdm(continue_nodes):       # 开始提取link
                links = extract_link_in_crossReference(nodes, node, links)
                links = extract_link_in_referencedEvent(nodes, node, links)
                links = extract_link_in_title(nodes, node, links)
                links = extract_link_in_body(nodes, node, links)
                links = extract_link_in_comment(nodes, node, links)
                if len(links) % 100 == 0:
                    file_opt.save_json_to_file(filepath + "links_type_sl.json", links)
            file_opt.save_json_to_file(filepath + "links_type_sl.json", links)
    elif renew == 0:
        links = file_opt.read_json_from_file(filepath + "links_type_sl.json")
    return

def visualization_multi_repos():
    # 多个repo可视化
    repolist = init.repos_to_get_info
    link_list = []
    for r_o in repolist:
        owner = r_o[0]
        name = r_o[1]
        links = file_opt.read_json_from_file(init.local_data_filepath+owner+"/"+name+"/links_type.json")
        link_list.append({"repo":owner+"/"+name, "links":links})
    vis.visualization_multi_type(link_list)
    vis.visualization_multi_where(link_list)
    vis.visualization_multi_when(link_list)
    return None


def work_on_repos(fullname_repo):
    owner, repo = fullname_repo[0], fullname_repo[1]
    print("--------------------handle " + owner + "/" + repo + "---------------------------")
    response_pr = file_opt.read_json_from_file(init.local_data_filepath+owner+"/"+repo+"/response_pullRequests.json")
    response_iss = file_opt.read_json_from_file(init.local_data_filepath+owner+"/"+repo+"/response_issues.json")
    extract_link_type(response_pr, response_iss, renew, init.local_data_filepath + owner + "/" + repo + "/")    # 主程序
    print("--------------------finish " + owner + "/" + repo + "---------------------------")

if __name__ == '__main__':
    from concurrent.futures import ThreadPoolExecutor as PoolExecutor
    repolist = init.repos_to_get_info
    with PoolExecutor(max_workers=5) as executor:
        for _ in executor.map(work_on_repos, repolist):
            pass