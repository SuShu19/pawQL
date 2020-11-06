import numpy as np
import matplotlib.pyplot as plt
from utils import file_opt
import init
from datetime import datetime

def extract_pr_iss_list(owner, repo):
    response_pr = file_opt.read_json_from_file(
        init.local_data_filepath + owner + "/" + repo + "/response_pullRequests.json")
    response_iss = file_opt.read_json_from_file(init.local_data_filepath + owner + "/" + repo + "/response_issues.json")
    pr_list, pr_createAt, issue_list, issue_createAt = [], [], [], []
    for item in response_pr['data']['repository']['pullRequests']['nodes']:
        pr_list.append(item['number'])
        pr_createAt.append(item['createdAt'])
    for item in response_iss['data']['repository']['issues']['nodes']:
        issue_list.append(item['number'])
        issue_createAt.append(item['createdAt'])
    return pr_list, pr_createAt, issue_list, issue_createAt


def visualization_type(links):
    pr_pr, pr_iss, iss_pr, iss_iss = [], [], [], []
    for link in links:
        if link['target']['type'] == "pullRequest to pullRequest":
            pr_pr.append(link)
        elif link['target']['type'] == "pullRequest to issue":
            pr_iss.append(link)
        elif link['target']['type'] == "issue to pullRequest":
            iss_pr.append(link)
        elif link['target']['type'] == "issue to issue":
            iss_iss.append(link)
        else:
            pass
    y = np.array([len(pr_pr),len(pr_iss),len(iss_pr),len(iss_iss)])
    x = ["pullRequest to pullRequest", "pullRequest to issue", "issue to pullRequest", "issue to issue"]
    plt.bar(x, y,color='cornflowerblue')
    plt.xticks(rotation = 10)
    for a, b in zip(x, y):
        plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=10)  # fontsize表示柱坐标上显示字体的大小
    plt.show()

def visualization_where(links):
    title, body, comment, review, cross_reference = [], [], [], [], []
    for link in links:
        if link['target']['location'] == "title":
            title.append(link)
        elif link['target']['location'] == "body":
            body.append(link)
        elif link['target']['location'] == "comment":
            comment.append(link)
        elif link['target']['location'] == "review":
            review.append(link)
        elif link['target']['location'] == "cross reference":
            cross_reference.append(link)
        else:
            pass
    y = np.array([len(title),len(body),len(comment),len(review),len(cross_reference)])
    x = ["title", "body", "comment", "review", "cross reference"]
    plt.bar(x, y,color='cornflowerblue')
    plt.xticks(rotation = 10)
    for a, b in zip(x, y):
        plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=10)  # fontsize表示柱坐标上显示字体的大小
    plt.show()

def visualization_when(links):
    time = []
    for link in links:
        time.append(link['target']['time_interval'])
    plt.hist(time, bins=50, color='cornflowerblue')         # 全体数据
    plt.show()

    time_s = sorted(time)
    time_cencored = time_s[time_s.index(-100):time_s.index(100)]   # 截取数据
    plt.hist(time_cencored,bins=50,color='cornflowerblue')
    plt.show()

def visualization_how_1_or_N(link_1_1, link_1_N):
    pr_pr_1_1,pr_pr_1_N = [], []
    pr_iss_1_1,pr_iss_1_N = [], []
    iss_pr_1_1,iss_pr_1_N = [], []
    iss_iss_1_1,iss_iss_1_N = [], []
    for link in link_1_1:
        if link['target'][0]['type'] == "pullRequest to pullRequest":
            pr_pr_1_1.append(link)
        elif link['target'][0]['type'] == "pullRequest to issue":
            pr_iss_1_1.append(link)
        elif link['target'][0]['type'] == "issue to pullRequest":
            iss_pr_1_1.append(link)
        elif link['target'][0]['type'] == "issue to issue":
            iss_iss_1_1.append(link)
        else:
            pass
    count = 0
    for link in link_1_N:
        for item in link['target']:
            count += 1
            if item['type'] == "pullRequest to pullRequest":
                pr_pr_1_N.append(link)
            elif item['type'] == "pullRequest to issue":
                pr_iss_1_N.append(link)
            elif item['type'] == "issue to pullRequest":
                iss_pr_1_N.append(link)
            elif item['type'] == "issue to issue":
                iss_iss_1_N.append(link)
            else:
                pass
    y1 = np.array([len(pr_pr_1_1),len(pr_iss_1_1),len(iss_pr_1_1),len(iss_iss_1_1)])
    y2 = np.array([len(pr_pr_1_N),len(pr_iss_1_N),len(iss_pr_1_N),len(iss_iss_1_N)])
    x = ["pullRequest to pullRequest", "pullRequest to issue", "issue to pullRequest", "issue to issue"]
    plt.bar(x, height=y2, bottom=y1, color='cornflowerblue', label='1 to N')
    plt.bar(x, height=y1, color='lightslategray', label='1 to 1')
    plt.xticks(rotation = 10)
    plt.legend()
    plt.show()


def visualization_how_self_or_bilateral(link_self_bilateral, link_bilateral):
    x = ["link to self", "bilateral link"]
    y = [len(link_self_bilateral),len(link_bilateral)]
    plt.bar(x, height=y, color='cornflowerblue')
    plt.show()

def visualization_how_cluster(link_cluster,owner,repo):
    layer_node, layer, node_num_list, node_list, node_interval, time_interval = [], [], [], [], [], []
    for link in link_cluster:
        nodes = []
        node_number = 0
        layer.append(len(link))
        for i in range(1,len(link)+1):
            node_number += len(link['layer_'+str(i)])
            for node in link['layer_'+str(i)]:
                nodes.append(node['source']['number'])
                for t in node['target']:
                    nodes.append(t["number"])
        node_num_list.append(node_number)
        node_interval.append([sorted(nodes)[0],sorted(nodes)[-1]])
        layer_node.append({"layer":len(link),"node":node_number})

    # 处理cluster最早的时间和最晚的时间之差
    pr_list, pr_createAt, issue_list, issue_createAt = extract_pr_iss_list(owner,repo)
    for link_s_e in node_interval:
        start, end = link_s_e[0], link_s_e[1]
        if start in pr_list:
            start_time = pr_createAt[pr_list.index(start)]
        else:
            start_time = issue_createAt[issue_list.index(start)]
        if end in pr_list:
            end_time = pr_createAt[pr_list.index(end)]
        else:
            end_time = issue_createAt[issue_list.index(end)]
        time_format = "%Y-%m-%dT%H:%M:%SZ"
        interval = datetime.strptime(end_time, time_format).__sub__(datetime.strptime(start_time,time_format)).days
        time_interval.append(interval)

    plt.hist(layer, bins=18, color='cornflowerblue')
    plt.title("layer number")
    plt.show()

    plt.hist(node_num_list, bins=100, color='cornflowerblue')
    plt.title("node number")
    plt.show()

    node_s = sorted(node_num_list)
    node_cencored = node_s[node_s.index(2):node_s.index(60)]   # 截取数据
    plt.hist(node_cencored,bins=50,color='cornflowerblue')
    plt.title("node number")
    plt.show()

    plt.hist(time_interval, bins=100, color='cornflowerblue')
    plt.title("time interval")
    plt.show()