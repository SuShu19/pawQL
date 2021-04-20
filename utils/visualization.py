import numpy as np
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
from utils import file_opt
from prepare import init
from datetime import datetime
from tqdm import tqdm
import seaborn as sns
import pandas as pd
from matplotlib import ticker as mticker
import math

seconds_a_minit = 60
seconds_in_day = 86400  # 取时间为天
# seconds_in_day = 1  # 取时间为秒
seconds_a_year = seconds_a_minit * 60 * 24 * 365
repo_list = ["Elasticsearch","Joomla-cms","Kubernetes","Pandas","Rails"]

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


def read_repos_data(file_name):
    repo_list = init.repo_list
    RQ_list = []
    for repo in repo_list:
        data = file_opt.read_json_from_file(init.local_data_filepath+repo.strip()+"/"+file_name)
        RQ_list.append(data)
    return RQ_list

def to_percent(temp, position):
    return '%1.0f'%(100*temp) + '%'

def auto_label(current_bar,former_bar=None):
    for i in range(0,len(current_bar)):
        height = current_bar[i].get_height()
        if height < 0.05:
            continue
        if former_bar is not None:
            base_height = 0
            for bars in former_bar:
                base_height += bars[i].get_height()
            plt.text(current_bar[i].get_x()+current_bar[i].get_width()/2.-0.2, 0.5*height+base_height, '%s%%' % round(float(100*height),2),color = "w",size=8)
        else:
            plt.text(current_bar[i].get_x()+current_bar[i].get_width()/2.-0.2, 0.5*height, '%s%%' % round(float(100*height),2),color = "w",size=8)

def plot_RQ1(dataset):
    # 层叠柱状图
    pr_pr_list, pr_iss_list, iss_pr_list, iss_iss_list = [],[],[],[]
    for repo_link in dataset:
        pr_pr, pr_iss, iss_pr, iss_iss = 0,0,0,0
        for link in repo_link:
            if link['target']['type'] == 'pullRequest to pullRequest':
                pr_pr += 1
            elif link['target']['type'] == 'pullRequest to issue':
                pr_iss += 1
            elif link['target']['type'] == 'issue to pullRequest':
                iss_pr += 1
            elif link['target']['type'] == 'issue to issue':
                iss_iss += 1

        pr_pr_list.append(pr_pr/len(repo_link))
        pr_iss_list.append(pr_iss/len(repo_link))
        iss_pr_list.append(iss_pr/len(repo_link))
        iss_iss_list.append(iss_iss/len(repo_link))

    pr_pr_list = np.array(pr_pr_list)
    pr_iss_list = np.array(pr_iss_list)
    iss_pr_list = np.array(iss_pr_list)
    iss_iss_list = np.array(iss_iss_list)

    # 绘制4个Type的图
    a = plt.bar(repo_list,height=pr_pr_list,bottom=iss_iss_list+iss_pr_list+pr_iss_list,color="gainsboro",label="P - P")
    b = plt.bar(repo_list,height=pr_iss_list,bottom=iss_iss_list+iss_pr_list,color="darkgray",label="P - I")
    c = plt.bar(repo_list,height=iss_pr_list,bottom=iss_iss_list,color="dimgrey",label="I - P")
    d = plt.bar(repo_list,height=iss_iss_list,bottom=0,color="black",label="I - I")
    auto_label(d)
    auto_label(c,former_bar=[d])
    auto_label(b,former_bar=[d,c])
    auto_label(a,former_bar=[d,b,c])
    plt.ylabel("Percentage of types")
    plt.ylim(0,1)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.legend(loc="upper right", ncol=4, bbox_to_anchor=(1, 1.1))
    plt.show()

def plot_RQ2(dataset):
    # 层叠柱状图
    title_body_list, commit_list, comment_list = [],[],[]
    for repo_link in dataset:
        title_body, commit, comment = 0, 0, 0
        for link in repo_link:
            if link['target']['location'] == 'title'or link['target']['location'] == 'body':
                title_body += 1
            elif link['target']['location'] == 'comment':
                comment += 1
            elif link['target']['location'] == 'commit':
                commit += 1
        title_body_list.append(title_body/len(repo_link))
        comment_list.append(comment/len(repo_link))
        commit_list.append(commit/len(repo_link))

    title_body_list = np.array(title_body_list)
    comment_list = np.array(comment_list)
    commit_list = np.array(commit_list)

    a = plt.bar(repo_list,height=comment_list,bottom=0,color="dimgrey",label="Comment")
    b = plt.bar(repo_list,height=title_body_list,bottom=comment_list,color="darkgray",label="Documentation")
    c = plt.bar(repo_list,height=commit_list,bottom=comment_list+title_body_list,color="gainsboro",label="Commit")
    auto_label(a)
    auto_label(b,former_bar=[a])
    auto_label(c,former_bar=[a,b])
    plt.ylim(0, 1)
    plt.ylabel("Percentage of locations")
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.legend(loc="upper right", ncol=3, bbox_to_anchor=(1, 1.1))
    plt.show()

def autolabel(rects,ax):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', size=8)

def plot_RQ3(dataset):
    # 层叠柱状图
    create_time_posi_list, create_time_neg_list, link_time_list = [],[],[]
    for repo_link in dataset:
        create_time_posi, create_time_neg, link_time = [], [], []
        for link in repo_link:
            ct = link["target"]["create_time_interval"]
            lt = link["target"]["link_time_interval"]
            if ct > 0:
                create_time_posi.append(ct/seconds_in_day)
            elif ct < 0:
                create_time_neg.append(-ct/seconds_in_day)
            elif ct-0 < 0.001:  # ct为0的情况
                create_time_neg.append((ct+1)/seconds_in_day)
            if lt >= 0:             # 把link time interval中为负的错误情况去除
                if lt-0 < 0.001:
                    link_time.append((lt + 1)/seconds_in_day)        # link time interval为0的变成1, 86400是一天中的秒数
                else:
                    link_time.append(lt/seconds_in_day)
            else:
                pass
        create_time_posi_list.append(create_time_posi)
        create_time_neg_list.append(create_time_neg)
        link_time_list.append(link_time)

    cnt_1_y, total = 0, 0
    for item in link_time_list:
        total += len(item)
        for value in item:
            if value > 31536000:
                cnt_1_y += 1
    print("link more than 1 year", ( cnt_1_y/total))

    create_posi_dic, create_neg_dic, link_dic, create_posi_len, create_neg_len = {}, {}, {}, [], []
    for i in range(0,len(repo_list)):
        create_posi_dic[repo_list[i].strip()] = create_time_posi_list[i]
        create_neg_dic[repo_list[i].strip()] = create_time_neg_list[i]
        link_dic[repo_list[i].strip()] = link_time_list[i]
        create_posi_len.append(len(create_time_posi_list[i]))
        create_neg_len.append(len(create_time_neg_list[i]))

    create_posi_dic = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in create_posi_dic.items()]))
    create_neg_dic = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in create_neg_dic.items()]))
    link_dic = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in link_dic.items()]))
    CTI = create_posi_dic.append(create_neg_dic)

    # 打印特征数据
    print("create time interval")
    print(CTI.describe())
    print("positive create time interval")
    print(create_posi_dic.describe())
    print("negative create time interval")
    print(create_neg_dic.describe())
    print("link time interval")
    print(link_dic.describe())

    # todo 对数的部分还是有问题，要在考虑一下，现在的时间是天
    create_posi_dic = create_posi_dic.apply(np.log10)
    create_neg_dic = create_neg_dic.apply(np.log10)
    link_dic = link_dic.apply(np.log10)

    sns.violinplot(data=create_posi_dic,color="Lightgrey", linewidth=1, cut=0)
    plt.yticks([math.log10(seconds_a_minit), math.log10(seconds_a_minit * 60), math.log10(seconds_a_minit * 60 * 24),
                math.log10(seconds_a_minit * 60 * 24 * 30), math.log10(seconds_a_minit * 60 * 24 * 365)],
               ['1 minite', '1 hour', '1 day', '1 month', '1 year'])
    plt.ylabel("Positive CTI (log)")
    plt.show()

    sns.violinplot(data=create_neg_dic,color="Lightgrey", linewidth=1, cut=0)
    plt.yticks([math.log10(seconds_a_minit), math.log10(seconds_a_minit * 60), math.log10(seconds_a_minit * 60 * 24),
                math.log10(seconds_a_minit * 60 * 24 * 30), math.log10(seconds_a_minit * 60 * 24 * 365)],
               ['1 minite', '1 hour', '1 day', '1 month', '1 year'])
    plt.ylabel("Negative CTI (log)")
    plt.show()

    sns.violinplot(data=link_dic,color="Lightgrey", linewidth=1, cut=0)
    plt.yticks([math.log10(seconds_a_minit), math.log10(seconds_a_minit * 60), math.log10(seconds_a_minit * 60 * 24),
                math.log10(seconds_a_minit * 60 * 24 * 30), math.log10(seconds_a_minit * 60 * 24 * 365)],
               ['1 minite', '1 hour', '1 day', '1 month', '1 year'])
    plt.ylabel("LTI (log)")
    plt.show()

    # 用百分比的图表示数据

    percent_neg, percent_posi = [], []
    for neg_item, posi_item in zip(create_neg_len, create_posi_len):
        percent_neg.append(neg_item / (neg_item + posi_item))
        percent_posi.append(posi_item / (neg_item + posi_item))

    create_neg_list = np.array(percent_neg)
    create_posi_list = np.array(percent_posi)

    a = plt.bar(repo_list,height=create_neg_list,bottom=0,color="dimgrey",label="Negative")
    b = plt.bar(repo_list,height=create_posi_list,bottom=create_neg_list,color="darkgray",label="Positive")
    auto_label(a)
    auto_label(b,former_bar=[a])
    plt.ylim(0, 1)
    plt.ylabel("Percentage of positive and negative CTI")
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.legend(loc="upper right", ncol=2, bbox_to_anchor=(1, 1.1))
    plt.show()

def plot_RQ4_1(RQ4_1_1,RQ4_1_n):
    '''multi-target link的可视化'''
    time_format = "%Y-%m-%dT%H:%M:%SZ"
    list_1_1, list_1_n, list_target_cnt = [], [], 0
    duration_1_1, duration_1_N = [], []
    for links in RQ4_1_1:
        sub_duration_1_1 = []
        list_1_1.append(len(links))
        for link in links:
            duration = abs(datetime.strptime(link['target'][0]['createdAt'],time_format).
                            __sub__(datetime.strptime(link['source']['createdAt'], time_format)).total_seconds())
            if duration < 0.001:
                duration = 1
            sub_duration_1_1.append(duration/seconds_in_day)
        duration_1_1.append(sub_duration_1_1)
    for links in RQ4_1_n:
        sub_duration_1_N = []
        count = 0
        for link in links:
            link_cti_list = []
            count += len(link['target'])
            link_cti_list.append(link['source']['createdAt'])
            for t in link['target']:
                link_cti_list.append(t['createdAt'])
            link_cti_list_s = sorted(link_cti_list, key=lambda data: get_time(data))
            sub_duration_1_N.append((datetime.strptime(link_cti_list_s[-1], time_format).__sub__(datetime.strptime(
                link_cti_list_s[0], time_format)).total_seconds())/seconds_in_day)
        list_1_n.append(count)
        duration_1_N.append(sub_duration_1_N)

    # 转成百分比
    for i in range(0,len(list_1_1)):
        sum = list_1_1[i] + list_1_n[i]
        list_1_1[i] = list_1_1[i] / sum
        list_1_n[i] = list_1_n[i] / sum

    # 画比例图
    a = plt.bar(repo_list,height=list_1_1,bottom=0,color="dimgrey",label="1 to 1")
    b = plt.bar(repo_list,height=list_1_n,bottom=list_1_1,color="darkgray",label="1 to N")
    auto_label(a)
    auto_label(b,former_bar=[a])
    plt.legend(loc="upper right", ncol=2, bbox_to_anchor=(1, 1.1))
    plt.ylabel("Percentage of link patterns")
    plt.ylim(0,1)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.legend(loc="upper right", ncol=2, bbox_to_anchor=(1, 1.1))
    plt.show()

    # 画时间持续的图
    duration_1_1_dic, duration_1_N_dic, = {}, {}
    for i in range(0,len(repo_list)):
        duration_1_1_dic[repo_list[i].strip()] = duration_1_1[i]
        duration_1_N_dic[repo_list[i].strip()] = duration_1_N[i]

    duration_1_1_dic = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in duration_1_1_dic.items()]))
    duration_1_N_dic = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in duration_1_N_dic.items()]))

    # 打印特征数据
    print("duration 1-1")
    print(duration_1_1_dic.describe())
    print("duration 1-N")
    print(duration_1_N_dic.describe())

    # todo 对数的部分还是有问题，要在考虑一下，现在的时间是天
    duration_1_1_dic = duration_1_1_dic.apply(np.log10)
    duration_1_N_dic = duration_1_N_dic.apply(np.log10)

    seconds_a_minit = 60

    sns.violinplot(data=duration_1_1_dic,color="Lightgrey", linewidth=1, cut=0)
    plt.yticks([math.log10(seconds_a_minit * 60 * 24),
                math.log10(seconds_a_minit * 60 * 24 * 30),
                math.log10(seconds_a_minit * 60 * 24 * 365),
                math.log10(seconds_a_minit * 60 * 24 * 365 * 5), ],
               ['1 day', '1 month', '1 year', '5 years'])
    plt.ylabel("Duration of singel-target links in days (log)")
    plt.show()

    sns.violinplot(data=duration_1_N_dic,color="Lightgrey", linewidth=1, cut=0)
    plt.yticks([math.log10(seconds_a_minit * 60 * 24),
                math.log10(seconds_a_minit * 60 * 24 * 30),
                math.log10(seconds_a_minit * 60 * 24 * 365),
                math.log10(seconds_a_minit * 60 * 24 * 365 * 5), ],
               ['1 day', '1 month', '1 year', '5 years'])
    plt.ylabel("Duration of multi-target links in days (log)")
    plt.show()

def plot_RQ4_2(RQ4_cluster):
    '''cluster的可视化'''
    layer_list, nodes_list, duration_list = {}, {}, {}
    for i in range(0,len(repo_list)):
        cluster_layer, cluster_node, duration, layer_equal_2, cluster_cnt = [], [], [], 0, 0
        cluster_cnt += len(RQ4_cluster[i])
        for cluster in RQ4_cluster[i]:
            if cluster["layers_count"] == 2:
                layer_equal_2 += 1
            cluster_layer.append(cluster["layers_count"])
            cluster_node.append(cluster["nodes_count"])
            if cluster["cluster_time_interval"] == 0:
                duration.append((cluster["cluster_time_interval"]+1)/seconds_in_day)
            else:
                duration.append((cluster["cluster_time_interval"])/seconds_in_day)
        layer_list[repo_list[i]] = cluster_layer
        nodes_list[repo_list[i]] = cluster_node
        duration_list [repo_list[i]] = sorted(duration)

    print("layer = 2 accounts for ", layer_equal_2 / cluster_cnt)

    layer_list = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in layer_list.items()]))
    nodes_list = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in nodes_list.items()]))
    duration_list = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in duration_list.items()]))

    # 显示数字特征
    print("cluster layer")
    print(layer_list.describe())
    print("cluster node")
    print(nodes_list.describe())
    print("cluster duration")
    print(duration_list.describe())

    # 对cluster的三个变量取对数
    # layer_list = layer_list.apply(np.log)
    # nodes_list = nodes_list.apply(np.log10)
    duration_list = duration_list.apply(np.log10)

    sns.violinplot(data=layer_list,color="Lightgrey", linewidth=1)
    plt.ylabel("Cluster depth")
    plt.show()

    sns.violinplot(data=nodes_list,color="Lightgrey", linewidth=1)
    plt.ylabel("Cluster size (log)")
    plt.show()

    seconds_a_minit = 60
    sns.violinplot(data=duration_list,color="Lightgrey", linewidth=1, cut=0)
    plt.yticks([math.log10(seconds_a_minit * 60 * 24),
                math.log10(seconds_a_minit * 60 * 24 * 30),
                math.log10(seconds_a_minit * 60 * 24 * 365),
                math.log10(seconds_a_minit * 60 * 24 * 365 * 5)],
               ['1 day','1 month', '1 year', '5 years'])
    plt.ylabel("Cluster duration (log)")
    plt.show()

def check_longest_link(dataset):
    for project in dataset:
        longest_link = project[0]
        for item in project:
            if item['target']['create_time_interval'] > longest_link['target']['create_time_interval']:
                longest_link = item
        print(longest_link)

if __name__ == '__main__':
    # 对论文中RQ1，2，3，4的结果进行汇总
    RQ1 = read_repos_data("links_type.json")
    sum = 0
    for item in RQ1:
        sum += len(item)
    RQ2 = RQ1
    RQ3 = RQ1
    RQ4_1_1 = read_repos_data("link_1_1.json")
    RQ4_1_n = read_repos_data("link_1_N.json")
    RQ4_cluster = read_repos_data("link_cluster.json")

    plot_RQ1(RQ1)
    # plot_RQ2(RQ2)
    # plot_RQ3(RQ3)
    # plot_RQ4_1(RQ4_1_1,RQ4_1_n)
    # plot_RQ4_2(RQ4_cluster)

    # check_longest_link(RQ1)