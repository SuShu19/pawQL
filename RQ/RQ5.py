import re
from datetime import datetime
import init
from utils import file_opt
from utils import visualization as vis
from prepare import prepare_response
from prepare import queries
from tqdm import tqdm
from prepare import preprocess

renew = 1

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

def parse_node2_in_url(url, location, node1,link_time, pr_list, pr_createAt, issue_list, issue_createAt,owner, name,target_author):
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
    return {'source':{'number': node1['number'], 'url': node1['url'], 'createdAt':node1['time'],},
            'target':{'number': int(node2_number), 'url': node2_url,
                      'times':[{'createdAt':node2_time,'link_author':target_author,'create_time_interval': create_time_interval,
                      "link_time_interval":link_time_interval,'type': link_type, 'location': location,
                      'isCrossRepository': isCrossRepository}]}}

def determine_number_type(pr_list, issue_list, number):
    if int(number) in pr_list:
        return "pullRequest"
    elif int(number) in issue_list:
        return "issue"
    else:
        return None

def determin_CR_link_location(source_number,target_number,source_type,source_owner,source_name,target_owner,target_name,target_url):
    print("request graphQL on ",target_number)
    r = prepare_response.query_request(queries.search_one_node, source_owner, source_name, source_type, number=source_number)
    location = None
    # 在body里面找link
    body_str = preprocess.clear_body(r['data']['repository'][source_type]['body'])
    if body_str.find(target_owner+"/"+target_name+"/"+str(target_number)) >= 0 or body_str.find(target_url)>=0:
        location = 'body'
    # 在comment里面找link
    for comment in r['data']['repository'][source_type]['comments']['nodes']:
        comment_str = preprocess.clear_body(comment['body'])
        if comment_str.find(target_owner+"/"+target_name+"/"+str(target_number)) >= 0 or comment_str.find(target_url)>=0:
            location = 'comment'
    return location

def parse_node2_in_num(quote_num, location, node1, owner, name, link_time, pr_list, pr_createAt, issue_list, issue_createAt,target_author):
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
    return {'source':{'number': node1['number'], 'url': node1['url'], 'createdAt':node1['time']},
            'target':{'number': int(node2_number), 'url': node2_url,
                      'times':[{'createdAt':node2_time, 'link_author':target_author ,'create_time_interval':create_time_interval,
                      'link_time_interval': link_time_interval,'type': link_type, 'location': location,
                      'isCrossRepository': isCrossRepository}]}}

def extract_pr_iss_list(response_p, response_i):
    pr_list, pr_createAt, issue_list, issue_createAt = [], [], [], []
    for item in response_p['data']['repository']['pullRequests']['nodes']:
        pr_list.append(item['number'])
        pr_createAt.append(item['createdAt'])
    for item in response_i['data']['repository']['issues']['nodes']:
        issue_list.append(item['number'])
        issue_createAt.append(item['createdAt'])
    return pr_list, pr_createAt, issue_list, issue_createAt

def detect_dup(links,link):
    repeat = 0
    if link:
        for i in range(len(links) - 1, 0, -1):
            if link['source']['number'] == links[i]['source']['number'] and \
                    link['target']['number'] == links[i]['target']['number']:
                repeat = 1  # 该link与之前的link重复
                links[i]['target']['times'].append(link['target']['times'][0])
                break
        if repeat == 0:
            links.append(link)
    return links

def extract_link_in_title(node, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt, links):
    # 处理title中#12345 link
    location = 'title'
    title_quote = re.findall(re.compile(r'#[0-9]+'), node['title'])
    link_time = node1['time']  # 在title里面发现的link都是在Node创建的时候就产生的，所以Link time=node create time
    try:
        author = node['author']['login']
    except TypeError:
        author = "ghost"
    if len(title_quote) != 0:
        for quote in title_quote:
            link = parse_node2_in_num(quote, location, node1, owner, name, link_time, pr_list, pr_createAt, issue_list, issue_createAt,author)
            links = detect_dup(links,link)
    return links

def extract_link_in_body(node, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt, links):
    # 处理body中的url link
    location = 'body'
    clean_body = preprocess.clear_body(node['body'])
    body_url = re.findall(re.compile(r'https://github.com/' + owner + '/' + name + '/+\w+/+[0-9]+'), clean_body)
    link_time = node1['time']  # 在title里面发现的link都是在Node创建的时候就产生的，所以Link time=node create time
    try:
        author = node['author']['login']
    except TypeError:
        author = "ghost"
    if len(body_url) != 0:
        for url in body_url:
            link = parse_node2_in_url(url, location, node1,link_time, pr_list, pr_createAt, issue_list, issue_createAt,owner, name, author)
            links = detect_dup(links,link)
    # 处理body中的#12345的link
    body_quote = re.findall(re.compile(r'#[0-9]+'), clean_body)
    if len(body_quote) != 0:
        for quote in body_quote:
            link = parse_node2_in_num(quote, location, node1, owner, name, link_time, pr_list, pr_createAt, issue_list, issue_createAt, author)
            links = detect_dup(links,link)
    return links

def extract_link_in_comment(node, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt, links):
    # 处理comment
    location = 'comment'
    if len(node['comments']['nodes']) != 0:
        for comment in node['comments']['nodes']:
            clean_comment = preprocess.clear_body(comment['body'])
            # 处理body中url的link
            comment_url = re.findall(re.compile(r'https://github.com/'+owner+'/'+name+'/+\w+/+[0-9]+'),clean_comment)
            link_time = comment['createdAt']
            try:
                author = comment['author']['login']
            except TypeError:
                author = "ghost"                # 账号被删除，用户名为None，github统一起名为ghost
            if len(comment_url) != 0:
                for url in comment_url:
                    link = parse_node2_in_url(url, location, node1,link_time,pr_list, pr_createAt, issue_list, issue_createAt,owner,name,author)
                    links = detect_dup(links,link)
            # 处理body中的#12345的link
            comment_quote = re.findall(re.compile(r'#[0-9]+'), clean_comment)
            if len(comment_quote) != 0:
                for quote in comment_quote:
                    link = parse_node2_in_num(quote, location, node1, owner, name, link_time,pr_list, pr_createAt, issue_list, issue_createAt,author)
                    links = detect_dup(links,link)
    return links

# def extract_link_in_review(node, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt, links):
#     # 处理comment
#     location = 'review'
#     if len(node['reviews']['nodes']) != 0:
#         for review in node['reviews']['nodes']:
#             review_comments = review['comments']['nodes']
#             for rc in review_comments:
#                 review_url = re.findall(re.compile(r'https://github.com/' + owner + '/' + name + '/+\w+/+[0-9]+'),
#                                         rc['body'])
#                 if len(review_url) != 0:
#                     location = 'review'
#                     for url in review_url:
#                         link = parse_node2_in_url(url, location, node1,pr_list, pr_createAt, issue_list, issue_createAt,owner,name)
#                         links = detect_dup(links,link)
#                 # 处理body中的#12345的link
#                 comment_quote = re.findall(re.compile(r'#[0-9]+'), rc['body'])
#                 if len(comment_quote) != 0:
#                     for quote in comment_quote:
#                         link = parse_node2_in_num(quote, location, node1, owner, name, pr_list, issue_list)
#                         links = detect_dup(links,link)
#     return links

def extract_link_in_crossReference(node, links,owner,name):
    # 处理crossReference
    for item in node['timelineItems']['nodes']:
        if item:
            if item['isCrossRepository'] == False:        # 只考虑其他repo通过crossReference连接过来的情况
                continue
            source_number = item['source']['number']
            source_url = item['source']['url']
            target_number = item['target']['number']
            target_url = item['target']['url']
            create_time_interval = datetime.strptime(item['target']['createdAt'], "%Y-%m-%dT%H:%M:%SZ").__sub__(
                datetime.strptime(item['source']['createdAt'], "%Y-%m-%dT%H:%M:%SZ")).days
            link_time_interval = datetime.strptime(item['referencedAt'], "%Y-%m-%dT%H:%M:%SZ").__sub__(
                datetime.strptime(item['source']['createdAt'], "%Y-%m-%dT%H:%M:%SZ")).days
            # 判断link type
            if "id" in item['source'].keys():
                source_type = "pullRequest"
            else:
                source_type = "issue"
            if "id" in item['target'].keys():
                target_type = "pullRequest"
            else:
                target_type = "issue"
            link_type = determine_link_type(source_type, target_type)
            source_owner = item['source']['repository']['owner']['login']
            source_name = item['source']['repository']['name']
            target_owner = item['target']['repository']['owner']['login']
            target_name = item['target']['repository']['name']
            try:
                link_author = node['author']['login']
            except TypeError:
                link_author = 'ghost'
            location = determin_CR_link_location(source_number,target_number,source_type,source_owner,source_name,target_owner,target_name,target_url)
            if location is None:        # source node中这条Link已经被删除，就不再考虑该Link
                continue
            print("find one: ",target_number)
            if source_type == target_type:
                pass
            else:
                if target_url.find('issues') == -1:
                    target_url = target_url.replace('pull', 'issues')
                elif target_url.find('pull') == -1:
                    target_url = target_url.replace('issues', 'pull')

            # 检测是否有重复的link
            repeat = 0
            for i in range(len(links) - 1, 0, -1):
                if source_number == links[i]['source']['number'] and target_number == links[i]['target']['number']:
                    repeat = 1  # 该link与之前的link重复
            if repeat == 0:
                links.append({'source':{'number': source_number, 'url': source_url, 'createdAt': item['source']['createdAt']},
                              'target':{'number': target_number, 'url': target_url,
                                        'times':[{'createdAt':item['target']['createdAt'],'link_author':link_author,
                                        'create_time_interval': create_time_interval,'link_time_interval':link_time_interval,
                                        'type': link_type, 'location': location, 'isCrossRepository': item['isCrossRepository']}]}})
    return links

def extract_link_type(response_p, response_i, renew, filepath=None):
    if renew == 1:
        type_list = ["pullRequests", "issues"]
        response_list = [response_p,response_i]
        links = []
        pr_list, pr_createAt, issue_list, issue_createAt = extract_pr_iss_list(response_p, response_i)
        owner = response_p['data']['repository']['owner']['login']
        name = response_p['data']['repository']['name']
        for response, type_ in zip(response_list, type_list):
            nodes = response['data']['repository'][type_]['nodes']
            # last_number = None
            # if Path(filepath+"links_type_title_RQ5.json").exists():
            #     links = file_opt.read_json_from_file(filepath+'links_type_title_RQ5.json')
            #     last_number = links[-1]['source']['number']
            for node in tqdm(nodes):
                # if last_number in vars():
                #     if node['number'] <= last_number:
                #         continue
                # 取出当前node的信息
                node1 = {'number': node["number"], 'url': node["url"], 'time': node["createdAt"], 'type': type_[:-1]}
                links = extract_link_in_title(node, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt, links)
                links = extract_link_in_body(node, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt, links)
                links = extract_link_in_comment(node, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt, links)
                links = extract_link_in_crossReference(node, links,owner,name)
        file_opt.save_json_to_file(filepath + "links_type_RQ5.json", links)
    elif renew == 0:
        links = file_opt.read_json_from_file(filepath + "links_type_RQ5.json")
    return links

def work_on_repos(fullname_repo):
    owner, name = fullname_repo[0], fullname_repo[1]
    print("--------------------handle " + owner + "/" + name + "---------------------------")
    response_pr = file_opt.read_json_from_file(init.local_data_filepath+owner+"/"+name+"/response_pullRequests.json")
    response_iss = file_opt.read_json_from_file(init.local_data_filepath+owner+"/"+name+"/response_issues.json")
    links = extract_link_type(response_pr, response_iss, renew, init.local_data_filepath + owner + "/" + name + "/")
    # vis.visualization_RQ5(links, repo=owner+"/"+name)

    # vis.visualization_type(links)
    # vis.visualization_where(links)
    # vis.visualization_when(links)

if __name__ == '__main__':
    from concurrent.futures import ThreadPoolExecutor as PoolExecutor
    repolist = init.repos_to_get_info
    with PoolExecutor(max_workers=1) as executor:
        for _ in executor.map(work_on_repos, repolist):
            pass