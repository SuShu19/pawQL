import numpy as np
import matplotlib.pyplot as plt
from utils import file_opt
from prepare import init
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

def visualization_when(links, repo=None):
    create_time, link_time = [], []
    for link in links:
        create_time.append(link['target']['create_time_interval'])
        link_time.append(link['target']['link_time_interval'])
    plt.hist(create_time, bins=50, color='cornflowerblue')
    plt.title("%s Create Time Interval" % repo)
    plt.show()

    plt.hist(link_time, bins=50, color='cornflowerblue')
    plt.title("%s Link Time Interval" % repo)
    plt.show()

    #
    # time_s = sorted(time)
    # time_cencored = time_s[time_s.index(-100):time_s.index(100)]   # 截取数据
    # plt.hist(time_cencored,bins=50,color='cornflowerblue')
    # plt.show()

def visualization_how_1_or_N(link_1_1, link_1_N, repo=None):
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
    y3 = np.array([len(pr_pr_1_1),len(pr_pr_1_N),len(pr_iss_1_1),len(pr_iss_1_N),
                   len(iss_pr_1_1),len(iss_pr_1_N),len(iss_iss_1_1),len(iss_iss_1_N)])
    x12 = ["pullRequest to pullRequest", "pullRequest to issue", "issue to pullRequest", "issue to issue"]
    x3 = ["pr-pr/1-1", "pr-pr/1-N", "pr-iss/1-1", "pr-iss/1-N", "iss-pr/1-1", "iss-pr/1-N", "iss-iss/1-1", "iss-iss/1-N"]

    plt.bar(x12, height=y2, bottom=y1, color='cornflowerblue', label='1 to N')
    plt.bar(x12, height=y1, color='lightslategray', label='1 to 1')
    plt.title("Link mode in 4 types")
    plt.xticks(rotation = 10)
    plt.legend()
    plt.show()

    plt.pie(y3, labels=x3, autopct='%1.2f%%', pctdistance=0.6, labeldistance=1.1, center=(0, 0),
            colors=('cornflowerblue', 'cornflowerblue', 'lightskyblue', 'lightskyblue', 'lightsteelblue','lightsteelblue','lavender','lavender'))
    plt.title("%s Link mode in 4 types" % repo)
    plt.show()

def visualization_how_self_or_bilateral(link_self_bilateral, link_bilateral, repo=None):
    x = ["link to self", "bilateral link"]
    y = [len(link_self_bilateral),len(link_bilateral)]
    plt.bar(x, height=y, color='cornflowerblue')
    plt.title("%s Link each other" % repo)
    plt.show()

def get_time(time):
    return datetime.strptime(time,"%Y-%m-%dT%H:%M:%SZ").timestamp()

def visualization_how_cluster(link_cluster, repo=None):
    node_num_list, layer, time_interval = [], [], []
    for link in tqdm(link_cluster):
        layer.append(link["layers_count"])
        node_num_list.append(link["nodes_count"])
        time_interval.append(link["cluster_time_interval"])

    plt.hist(layer, bins=18, color='cornflowerblue')
    plt.title("%s layer number" % repo)
    plt.show()

    plt.hist(node_num_list, bins=100, color='cornflowerblue')
    plt.title("%s node number" % repo)
    plt.show()

    # node_s = sorted(node_num_list)
    # print(node_s)
    # node_cencored = node_s[node_s.index(2):node_s.index(50)]   # 截取数据
    # plt.hist(node_cencored,bins=30,color='cornflowerblue')
    # plt.title("%s node number (cencored 30)" % repo)
    # plt.show()


    plt.hist(time_interval, bins=100, color='cornflowerblue')
    plt.title("%s time interval" % repo)
    plt.show()

    time_interval_s = sorted(time_interval)
    print(time_interval_s)

def visualization_RQ5(links,repo=None):
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
        if len(link['target']['times']) == 271:
            print(link)

    print(sorted(times))
    plt.hist(times,bins=20,color='cornflowerblue')
    plt.title("%s link times" % repo)
    plt.show()

    print(sorted(author))
    plt.hist(author,bins=max(author),color='cornflowerblue')
    plt.xticks(range(1,max(author)+1,1))
    plt.title("%s link authors" % repo)
    plt.show()

def visualization_multi_type(link_list):
    for repo_link in link_list:
        pr_pr, pr_iss, iss_pr, iss_iss = [], [], [], []
        for link in repo_link['links']:
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
        x = ["pr to pr", "pr to iss", "iss to pr", "iss to iss"]
        plt.pie(y,labels=x,autopct='%1.2f%%',colors=('cornflowerblue', 'lightskyblue', 'lightsteelblue', 'lavender'), pctdistance=0.6, labeldistance=1.1, center = (0, 0) )
        plt.title("%s Link Type" % repo_link['repo'])
        plt.xticks(rotation = 10)
        plt.show()


def visualization_multi_where(link_list):
    for repo_link in link_list:
        title, body, comment = [], [], []
        for link in repo_link['links']:
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
        plt.pie(y,labels=x,autopct='%1.2f%%',colors=('cornflowerblue', 'lightskyblue', 'lightsteelblue'), pctdistance=0.6, labeldistance=1.1, center = (0, 0) )
        plt.title("%s Link Location" % repo_link['repo'])
        plt.xticks(rotation = 10)
        plt.show()

def visualization_multi_when(link_list):
    for repo_link in link_list:
        visualization_when(repo_link["links"],repo_link['repo'])


def visualization_multi_self_bila(link_list):
    x, y_s, y_b = [], [], []
    for repo_link in link_list:
        # 输入统计数据
        x.append(repo_link['repo'])
        y_s.append(len(repo_link['link_self']))
        y_b.append(len(repo_link['link_bilateral']))

    bar_width = 0.3  # 条形宽度
    index_link_self = np.arange(len(x))  # 男生条形图的横坐标
    index_link_bil = index_link_self + bar_width  # 女生条形图的横坐标

    # 使用两次 bar 函数画出两组条形图
    plt.bar(index_link_self, height=y_s, width=bar_width, color='cornflowerblue', label='link_to_self')
    plt.bar(index_link_bil, height=y_b, width=bar_width, color='lightsteelblue', label='link_to_each_other')

    plt.legend()  # 显示图例
    plt.xticks(index_link_self + bar_width / 2, x)  # 让横坐标轴刻度显示 waters 里的饮用水， index_male + bar_width/2 为横坐标轴刻度的位置
    plt.title('link to slef or each other')  # 图形标题

    plt.show()
