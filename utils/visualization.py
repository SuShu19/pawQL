import numpy as np
import matplotlib.pyplot as plt
from utils import file_opt
import init
from datetime import datetime
from tqdm import tqdm

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
    plt.title("Link Type")
    plt.xticks(rotation = 10)
    for a, b in zip(x, y):
        plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=10)  # fontsize表示柱坐标上显示字体的大小
    plt.show()

def visualization_where(links):
    title, body, comment = [], [], []
    for link in links:
        if link['target']['location'] == "title":
            title.append(link)
        elif link['target']['location'] == "body":
            body.append(link)
        elif link['target']['location'] == "comment":
            comment.append(link)
        else:
            pass
    y = np.array([len(title),len(body),len(comment)])
    x = ["title", "body", "comment"]
    plt.bar(x, y,color='cornflowerblue')
    plt.title("Link Location")
    plt.xticks(rotation = 10)
    for a, b in zip(x, y):
        plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=10)  # fontsize表示柱坐标上显示字体的大小
    plt.show()

def visualization_when(links):
    create_time, link_time = [], []
    for link in links:
        create_time.append(link['target']['create_time_interval'])
        link_time.append(link['target']['link_time_interval'])
    plt.hist(create_time, bins=50, color='cornflowerblue')
    plt.title("Create Time Interval")
    plt.show()

    plt.hist(link_time, bins=50, color='cornflowerblue')
    plt.title("Link Time Interval")
    plt.show()

    #
    # time_s = sorted(time)
    # time_cencored = time_s[time_s.index(-100):time_s.index(100)]   # 截取数据
    # plt.hist(time_cencored,bins=50,color='cornflowerblue')
    # plt.show()

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
    plt.title("Link mode in 4 types")
    plt.xticks(rotation = 10)
    plt.legend()
    plt.show()


def visualization_how_self_or_bilateral(link_self_bilateral, link_bilateral):
    x = ["link to self", "bilateral link"]
    y = [len(link_self_bilateral),len(link_bilateral)]
    plt.bar(x, height=y, color='cornflowerblue')
    plt.title("Link each other")
    plt.show()

def get_time(time):
    return datetime.strptime(time,"%Y-%m-%dT%H:%M:%SZ").timestamp()

def visualization_how_cluster(link_cluster,owner,repo):
    layer_node, layer, node_num_list, node_list, node_interval, time_interval = [], [], [], [], [],[]
    for link in tqdm(link_cluster):
        nodes = []
        node_number = 0
        layer.append(len(link))
        for i in range(1,len(link)+1):
            time_list = []
            node_number += len(link['layer_'+str(i)])
            for node in link['layer_'+str(i)]:
                nodes.append(node['source']['number'])
                time_list.append(node['source']['createdAt'])
                for t in node['target']:
                    nodes.append(t["number"])
                    time_list.append(t['createdAt'])
        node_num_list.append(node_number)
        time_interval_s = sorted(time_list,key=lambda data:get_time(data))
        time_format = "%Y-%m-%dT%H:%M:%SZ"
        time_interval.append(datetime.strptime(time_interval_s[-1], time_format).__sub__(datetime.strptime(time_interval_s[0],time_format)).days)
        node_interval.append([sorted(nodes)[0],sorted(nodes)[-1]])
        layer_node.append({"layer":len(link),"node":node_number})

    plt.hist(layer, bins=18, color='cornflowerblue')
    plt.title("layer number")
    plt.show()

    plt.hist(node_num_list, bins=100, color='cornflowerblue')
    plt.title("node number")
    plt.show()

    node_s = sorted(node_num_list)
    print(node_s)
    node_cencored = node_s[node_s.index(2):node_s.index(50)]   # 截取数据
    plt.hist(node_cencored,bins=30,color='cornflowerblue')
    plt.title("node number (cencored 30)")
    plt.show()


    plt.hist(time_interval, bins=100, color='cornflowerblue')
    plt.title("time interval")
    plt.show()

    time_interval_s = sorted(time_interval)
    print(time_interval_s)

def visualization_RQ5(links):
    times, author = [], []
    for link in links:
        author_each_link = []
        times.append(len(link['target']['times']))
        author_each_link.append(link['target']['times'][0]['link_author'])
        if len(link['target']['times']) > 1:
            for i in range(1,len(link['target']['times'])):
                if link['target']['times'][i]['link_author'] not in author_each_link:
                    author_each_link.append(link['target']['times'][i]['link_author'])
        author.append(len(author_each_link))

    print(sorted(times))
    plt.hist(times,bins=20,color='cornflowerblue')
    plt.title("link times")
    plt.show()

    print(sorted(author))
    plt.hist(author,bins=6,color='cornflowerblue')
    plt.title("link authors")
    plt.show()

