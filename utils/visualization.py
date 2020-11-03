import numpy as np
import matplotlib.pyplot as plt

def plot_link_classes(pr_pr,pr_iss,iss_pr,iss_iss):
    y1 = np.array([len(pr_pr),len(pr_iss)])
    y2 = np.array([len(iss_pr),len(iss_iss)])
    y2 = np.array([len(iss_pr),len(iss_iss)])
    x = ["pullRequests", "issues"]
    plt.bar(x, y1,color='cornflowerblue',label='link to pullRequests')
    plt.bar(x, y2,color='lightslategray',label='link to issues')
    plt.legend()
    plt.show()

def plot_link_time(pr_pr,pr_iss,iss_pr,iss_iss):
    time_list = []
    for item in pr_pr+pr_iss+iss_pr+iss_iss:
        time_list.append(item['timeInterval'])
    y = np.array(time_list)
    plt.hist(y,bins=10,color='lightslategray')
    plt.legend()
    plt.show()

    # 截尾
    time_list = sorted(time_list)
    time_list_cencored = time_list[:time_list.index(800)]
    plt.hist(time_list_cencored,bins=50,color='lightslategray')
    plt.show()

    #箱图
    # plt.boxplot(time_list,sym='.',showmeans=True)
    # plt.show()
    #
    # plt.boxplot(time_list_cencored,sym='.')
    # plt.show()



def plot_link_mode(dataset):
    y1 = np.array([len(dataset[0]),len(dataset[3]),len(dataset[6]),len(dataset[9])])
    y2 = np.array([len(dataset[1]),len(dataset[4]),len(dataset[7]),len(dataset[10])])
    # y3 = np.array([len(dataset[2]),len(dataset[5]),len(dataset[6]),len(dataset[11])])
    x = ["pr2pr","pr2iss", "iss2pr", "iss2iss"]
    plt.bar(x, y1,color='cornflowerblue',label='1 to 1')
    plt.bar(x, y2,color='lightslategray',label='1 to N')
    # plt.bar(x, y3,color='bisque',label='1 to 1 to 1')
    plt.legend()
    plt.show()

def plot_link_num(dataset):
    num_list = []
    for item in dataset:
        num_list.append(len(item['target']))
    y = np.array(num_list)
    plt.hist(y,bins=40,color='lightslategray')
    plt.show()




































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

def visualization_how_cluster(link_cluster):
    layer_node, layer, node_list = [], [], []
    for link in link_cluster:
        node_number = 0
        layer.append(len(link))
        for i in range(1,len(link)+1):
            node_number += len(link['layer_'+str(i)])
        node_list.append(node_number)
        layer_node.append({"layer":len(link),"node":node_number})
    plt.hist(layer, bins=18, color='cornflowerblue')
    plt.title("layer number")
    plt.show()

    plt.hist(node_list, bins=100, color='cornflowerblue')
    plt.title("node number")
    plt.show()

    node_s = sorted(node_list)
    node_cencored = node_s[node_s.index(1):node_s.index(60)]   # 截取数据
    plt.hist(node_cencored,bins=50,color='cornflowerblue')
    plt.title("node number")
    plt.show()