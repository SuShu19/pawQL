import re
from datetime import datetime
import init
from utils import file_opt
import numpy as np
import matplotlib.pyplot as plt
from utils import visualization as vis

renew = 0

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

def parse_node2_in_url(url, location, node1,pr_list, pr_createAt, issue_list, issue_createAt,owner, name):
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

    time_interval = datetime.strptime(node1['time'], "%Y-%m-%dT%H:%M:%SZ") \
        .__sub__(datetime.strptime(node2_time, "%Y-%m-%dT%H:%M:%SZ")).days
    link_type = determine_link_type(node1["type"], node2_type)
    if node1['url'].split("/")[:5] == node2_url.split("/")[:5]:
        isCrossRepository = False
    else:
        isCrossRepository = True
    return {'source':{'number': node1['number'], 'source_url': node1['url']},
            'target':{'number': int(node2_number), 'target_url': node2_url,'time_interval': time_interval,
                      'type': link_type, 'location': location, 'isCrossRepository': isCrossRepository}}

def determine_number_type(pr_list, issue_list, number):
    if int(number) in pr_list:
        return "pullRequest"
    elif int(number) in issue_list:
        return "issue"
    else:
        return None

def parse_node2_in_num(quote_num, location, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt,):
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
    time_interval = datetime.strptime(node2_time, "%Y-%m-%dT%H:%M:%SZ") \
        .__sub__(datetime.strptime(node1['time'], "%Y-%m-%dT%H:%M:%SZ")).days
    link_type = determine_link_type(node1["type"], node2_type)
    if node1['url'].split("/")[:5] == node2_url.split("/")[:5]:
        isCrossRepository = False
    else:
        isCrossRepository = True
    return {'source':{'number': node1['number'], 'source_url': node1['url']},
            'target':{'number': int(node2_number), 'target_url': node2_url, 'time_interval': time_interval,
                      'type': link_type, 'location': location, 'isCrossRepository': isCrossRepository}}

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
        if repeat == 0:
            links.append(link)
    return links

def extract_link_in_title(node, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt, links):
    # 处理title中#12345 link
    location = 'title'
    title_quote = re.findall(re.compile(r'#[0-9]+'), node['title'])
    if len(title_quote) != 0:
        for quote in title_quote:
            link = parse_node2_in_num(quote, location, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt)
            links = detect_dup(links,link)
    return links

def extract_link_in_body(node, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt, links):
    # 处理body中的url link
    location = 'body'
    body_url = re.findall(re.compile(r'https://github.com/' + owner + '/' + name + '/+\w+/+[0-9]+'), node['body'])
    if len(body_url) != 0:
        for url in body_url:
            link = parse_node2_in_url(url, location, node1,pr_list, pr_createAt, issue_list, issue_createAt,owner, name)
            links = detect_dup(links,link)
    # 处理body中的#12345的link
    body_quote = re.findall(re.compile(r'#[0-9]+'), node['body'])
    if len(body_quote) != 0:
        for quote in body_quote:
            link = parse_node2_in_num(quote, location, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt)
            links = detect_dup(links,link)
    return links

def extract_link_in_comment(node, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt, links):
    # 处理comment
    location = 'comment'
    if len(node['comments']['nodes']) != 0:
        for comment in node['comments']['nodes']:
            comment_url = re.findall(re.compile(r'https://github.com/'+owner+'/'+name+'/+\w+/+[0-9]+'),comment['body'])
            if len(comment_url) != 0:
                for url in comment_url:
                    link = parse_node2_in_url(url, location, node1,pr_list, pr_createAt, issue_list, issue_createAt,owner,name)
                    links = detect_dup(links,link)
            # 处理body中的#12345的link
            comment_quote = re.findall(re.compile(r'#[0-9]+'), comment['body'])
            if len(comment_quote) != 0:
                for quote in comment_quote:
                    link = parse_node2_in_num(quote, location, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt)
                    links = detect_dup(links,link)
    return links

def extract_link_in_review(node, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt, links):
    # 处理comment
    location = 'review'
    if len(node['reviews']['nodes']) != 0:
        for review in node['reviews']['nodes']:
            review_comments = review['comments']['nodes']
            for rc in review_comments:
                review_url = re.findall(re.compile(r'https://github.com/' + owner + '/' + name + '/+\w+/+[0-9]+'),
                                        rc['body'])
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

def extract_link_in_crossReference(node, links):
    # 处理crossReference
    for item in node['timelineItems']['nodes']:
        location = 'cross reference'
        if item:
            source_number = item['source']['number']
            source_url = item['source']['url']
            target_number = item['target']['number']
            target_url = item['target']['url']
            time_interval = datetime.strptime(item['referencedAt'], "%Y-%m-%dT%H:%M:%SZ").__sub__(
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


            if source_type == target_type:
                pass
            else:
                if target_url.find('issues') == -1:
                    target_url = target_url.replace('pull', 'issues')
                elif target_url.find('pull') == -1:
                    target_url = target_url.replace('issues', 'pull')
            repeat = 0
            for i in range(len(links) - 1, 0, -1):
                if source_number == links[i]['source'] and target_number == links[i]['target']:
                    repeat = 1  # 该link与之前的link重复
            if repeat == 0:
                links.append({'source':{'number': source_number, 'source_url': source_url},
                              'target':{'number': target_number, 'target_url': target_url, 'time_interval': time_interval,
                                        'type': link_type, 'location': location, 'isCrossRepository': item['isCrossRepository']}})

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
            for node in nodes:
                # 取出当前node的信息
                node1 = {'number': node["number"], 'url': node["url"], 'time': node["createdAt"], 'type': type_[:-1]}
                links = extract_link_in_title(node, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt, links)
                links = extract_link_in_body(node, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt, links)
                links = extract_link_in_comment(node, node1, owner, name, pr_list, pr_createAt, issue_list, issue_createAt, links)
                links = extract_link_in_crossReference(node, links)
        file_opt.save_json_to_file(filepath + "links_type.json", links)
    elif renew == 0:
        links = file_opt.read_json_from_file(filepath + "links_type.json")
    return links

def work_on_repos(renew):
    for o_r in init.repos_to_get_info:
        owner, repo = o_r[0], o_r[1]
        print("--------------------handle " + owner + "/" + repo + "---------------------------")
        response_pr = file_opt.read_json_from_file(init.local_data_filepath+owner+"/"+repo+"/response_pullRequests.json")
        response_iss = file_opt.read_json_from_file(init.local_data_filepath+owner+"/"+repo+"/response_issues.json")
        links = extract_link_type(response_pr, response_iss, renew, init.local_data_filepath + owner + "/" + repo + "/")
    return links

if __name__ == '__main__':
    links = work_on_repos(renew)
    vis.visualization_type(links)
    vis.visualization_where(links)
    vis.visualization_when(links)