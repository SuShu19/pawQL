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
from py2neo import Graph, Node, Relationship, NodeMatcher
import py2neo
import shutil

g = Graph('http://localhost:7474', user="neo4j", password="native-orchid-match-virus-parking-5393")
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

def extract_relations_in_title(pr_list, issue_list, node, develop_unit):
    title = Node("title", content=node['title'])  # 创建标题实体
    g.merge(title, 'title', "content")
    g.merge(Relationship(develop_unit, "title", title))

    title_quote = re.findall(re.compile(r'#[0-9]+'), node['title'])
    if title_quote != []:
        for quote in title_quote:
            target_number = quote.replace("#",'')
            for item in pr_list:
                if str(item) == str(target_number):
                    target_node = Node("pullRequest", number=str(target_number))  # 创建单元实体
                    g.merge(target_node, "pullRequest", 'number')
                    g.merge(Relationship(title, "linkTo", target_node))
                    continue
            for item in issue_list:
                if str(item) == str(target_number):
                    target_node = Node("issue", number=str(target_number))  # 创建单元实体
                    g.merge(target_node, "issue", 'number')
                    g.merge(Relationship(title, "linkTo", target_node))
                    continue


def extract_relations_in_body(pr_list, issue_list, node, develop_unit):

    body = Node("body", content=node['body'])  # 创建标题实体
    g.merge(body, 'body', "content")
    g.merge(Relationship(develop_unit, "body", body))

    body_link, body_url = [], []
    body_url += re.findall(re.compile(r'https://github.com/' + node['url'].split('/')[-4] + '/' + node['url'].split('/')[-3] + '/+pull+/+[0-9]+'), preprocess.clear_body(node['body']))
    body_url += re.findall(re.compile(r'https://github.com/' + node['url'].split('/')[-4] + '/' + node['url'].split('/')[-3] + '/+issues+/+[0-9]+'), preprocess.clear_body(node['body']))
    if len(body_url) != 0:
        for url in body_url:
            body_link.append(url.split('/')[-1])
    body_quote = re.findall(re.compile(r'#[0-9]+'), preprocess.clear_body(node['body']))
    if len(body_quote) != 0:
        for quote in body_quote:
            body_link.append(quote.replace("#", ""))

    if body_link != []:
        for target_number in body_link:
            for item in pr_list:
                if str(item) == str(target_number):
                    target_node = Node("pullRequest", number=str(target_number))  # 创建单元实体
                    g.merge(target_node, "pullRequest", 'number')
                    g.merge(Relationship(body, "linkTo", target_node))
                    continue
            for item in issue_list:
                if str(item) == str(target_number):
                    target_node = Node("issue", number=str(target_number))  # 创建单元实体
                    g.merge(target_node, "issue", 'number')
                    g.merge(Relationship(body, "linkTo", target_node))
                    continue

def extract_relations_in_comment(pr_list, issue_list, node, develop_unit):
    for comment in node['comments']['nodes']:

        comment_node = Node("comment", content=comment['body'])  # 创建标题实体
        g.merge(comment_node, 'comment', "content")
        g.merge(Relationship(develop_unit, "comment", comment_node))

        if comment['author'] is not None:
            author = Node("author", name=comment['author']['login'])  # 创建用户实体
            g.merge(author, 'author', "name")
            g.merge(Relationship(author, "create", comment_node))
        else:
            pass

        time = Node("time", time=comment['createdAt'])  # 创建时间实体
        g.merge(time, 'time', "time")
        g.merge(Relationship(comment_node, "time", time))

        comment_link, comment_url = [], []
        comment_url += re.findall(re.compile(r'https://github.com/' + node['url'].split('/')[-4] + '/' + node['url'].split('/')[-3] + '/+pull+/+[0-9]+'), preprocess.clear_body(comment['body']))
        comment_url += re.findall(re.compile(r'https://github.com/' + node['url'].split('/')[-4] + '/' + node['url'].split('/')[-3] + '/+issues+/+[0-9]+'), preprocess.clear_body(comment['body']))
        if len(comment_url) != 0:
            for url in comment_url:
                comment_link.append(url.split('/')[-1])
        comment_quote = re.findall(re.compile(r'#[0-9]+'), preprocess.clear_body(comment['body']))
        if len(comment_quote) != 0:
            for quote in comment_quote:
                comment_link.append(quote.replace("#",""))

        for target_number in comment_link:
            if target_number == develop_unit['number']:
                continue
            for item in pr_list:
                if str(item) == str(target_number):
                    target_node = Node("pullRequest", number=str(target_number))  # 创建单元实体
                    g.merge(target_node, "pullRequest", 'number')
                    g.merge(Relationship(comment_node, "linkTo", target_node))
                    continue
            for item in issue_list:
                if str(item) == str(target_number):
                    target_node = Node("issue", number=str(target_number))  # 创建单元实体
                    g.merge(target_node, "issue", 'number')
                    g.merge(Relationship(comment_node, "linkTo", target_node))
                    continue


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

def extract_relations_in_crossReference(node, develop_unit):
    # 处理crossReference, 从target找source
    for item in node['timelineItems']['nodes']:
        if item:
            if "source" not in item:                      # 排除ReferencedAt的情况
                continue
            source_number = item['source']['number']
            source_url = item['source']['url']
            source_type = extract_type_in_url(source_url)

            source_node = Node(source_type, number=source_number, url=source_url)  # 创建节点实体
            g.merge(source_node, source_type, "number")
            g.merge(Relationship(source_node, "linkTo", develop_unit))


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

def extract_relations_in_referencedEvent(node, develop_unit):
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

def find_break(owner, repo):
    filefolder = '../data/' + owner + "/" + repo
    if not os.path.exists(filefolder + '/pullRequests.txt') :
        os.makedirs(filefolder)
        file = open(filefolder + '/pullRequests.txt','w')
        file.close()
    if not os.path.exists(filefolder + '/issues.txt'):
        file = open(filefolder + '/issues.txt','w')
        file.close()
    last_pr = file_opt.read_lastline_in_file(filefolder + '/pullRequests.txt')
    last_issue = file_opt.read_lastline_in_file(filefolder + '/issues.txt')
    return last_pr, last_issue

def create_noe4j(response_p, response_i, renew, owner, repo, filepath=None):
    # 断点重启
    last_pr_number, last_issue_number = find_break(owner, repo)
    # 确定pr号和issue号的列表
    pr_list = []
    for node in response_p['data']['repository']['pullRequests']['nodes']:
        pr_list.append(node['number'])
    issue_list = []
    for node in response_i['data']['repository']['issues']['nodes']:
        issue_list.append(node['number'])

    for nodes, node_type, last_number in zip([response_p,response_i],['pullRequests', 'issues'], [last_pr_number, last_issue_number]):
        for node in tqdm(nodes['data']['repository'][node_type]['nodes']):
            if last_number is not None:
                if node['number'] <= int(last_number):
                    continue
            else:
                pass
            develop_unit = Node(node_type[:-1], number=str(node['number']), url=node['url'])     # 创建单元实体
            g.merge(develop_unit, node_type[:-1], 'number')
            if node['author'] is not None:     # 创建用户实体和用户与单元关系
                author = Node("author", name=node['author']['login'])
                g.merge(author, "author", "name")
                g.merge(Relationship(author, 'create', develop_unit))
            else:
                pass
            time = Node("time", time=node['createdAt'])    # 创建时间实体
            g.merge(time, 'time', "time")
            g.merge(Relationship(develop_unit,"time",time))

            extract_relations_in_title(pr_list, issue_list, node, develop_unit)
            extract_relations_in_body(pr_list, issue_list, node, develop_unit)
            extract_relations_in_comment(pr_list, issue_list, node, develop_unit)
            # extract_relations_in_crossReference(node, develop_unit)   # 要找到link的位置，暂时不用
            # extract_relations_in_referencedEvent(node, develop_unit)  # 要找到link的位置，暂时不用

            file_opt.save_line_to_file('../data/' + owner + "/" + repo + "/" + node_type + '.txt', str(node['number']))
    # 删除记录number的2个文件
    shutil.rmtree("../data/" + owner)


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

def calculate_detail(node, comment_cnt, ref_event, cross_event):
    comment_cnt += len(node['comments']['nodes'])
    for timeline in node['timelineItems']['nodes']:
        if timeline is not None:
            if 'commitRepository' in timeline:
                ref_event += 1
            else:
                cross_event += 1
    return comment_cnt, ref_event, cross_event

def calculate_data_number(pr,issue):
    comment_cnt, ref_event, cross_event = 0, 0, 0
    for node in pr['data']['repository']['pullRequests']['nodes']:
        comment_cnt, ref_event, cross_event = calculate_detail(node, comment_cnt, ref_event, cross_event)
    for node in issue['data']['repository']['issues']['nodes']:
        comment_cnt, ref_event, cross_event = calculate_detail(node, comment_cnt, ref_event, cross_event)
    print("comment number, referencedEvent number, crossReferencedEvent number:", comment_cnt, ref_event, cross_event)

def work_on_repos(fullname_repo):
    owner, repo = fullname_repo[0], fullname_repo[1]
    print("--------------------handle " + owner + "/" + repo + "---------------------------")
    response_pr = file_opt.read_json_from_file(init.local_data_filepath+owner+"/"+repo+"/response_pullRequests.json")
    response_iss = file_opt.read_json_from_file(init.local_data_filepath+owner+"/"+repo+"/response_issues.json")
    create_noe4j(response_pr, response_iss, renew, owner, repo, init.local_data_filepath + owner + "/" + repo + "/")    # 主程序
    print("--------------------finish " + owner + "/" + repo + "---------------------------")

if __name__ == '__main__':
    from concurrent.futures import ThreadPoolExecutor as PoolExecutor
    repolist = init.repos_to_get_info
    with PoolExecutor(max_workers=5) as executor:
        for _ in executor.map(work_on_repos, repolist):
            pass