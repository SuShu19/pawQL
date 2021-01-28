import sys
sys.path.append('/home/zhangyu/pawQL/')  #导入文件夹的.py文件
from utils import file_opt
from prepare import init
from tqdm import tqdm
from utils import visualization as vis
from datetime import datetime

renew = 1

def extract_link_mode(linkset,renew,save_file_path):
    if renew == 1:
        link_1_1, link_1_N = parse_1_and_N(linkset)
        link_cluster = parse_link_cluster(link_1_1,link_1_N)
        link_self_bilateral, link_bilateral = parse_bilateral(linkset)

        file_opt.save_json_to_file(save_file_path+"link_1_1.json",link_1_1)
        file_opt.save_json_to_file(save_file_path+"link_1_N.json",link_1_N)
        file_opt.save_json_to_file(save_file_path+"link_bi.json",link_bilateral)
        file_opt.save_json_to_file(save_file_path+"link_self_bi.json",link_self_bilateral)
        file_opt.save_json_to_file(save_file_path+"link_cluster.json",link_cluster)
    elif renew == 0:
        link_1_1 = file_opt.read_json_from_file(save_file_path+"link_1_1.json")
        link_1_N = file_opt.read_json_from_file(save_file_path+"link_1_N.json")
        link_self_bilateral = file_opt.read_json_from_file(save_file_path+"link_self_bi.json")
        link_bilateral = file_opt.read_json_from_file(save_file_path+"link_bi.json")
        link_cluster = file_opt.read_json_from_file(save_file_path+"link_cluster.json")
    return link_1_1, link_1_N, link_self_bilateral, link_bilateral, link_cluster


def extract_number_list(linkset):
    number_list = []
    for link in linkset:
        number_list.append(link['source']['number'])
    return number_list

def get_time(time):
    return datetime.strptime(time,"%Y-%m-%dT%H:%M:%SZ").timestamp()

def parse_link_cluster(link_1_1,link_1_N):
    source_number_11_list = extract_number_list(link_1_1)
    source_number_1N_list = extract_number_list(link_1_N)
    number_list = source_number_11_list + source_number_1N_list
    linkset = link_1_1+link_1_N
    cluster_list = []
    search_linkset = linkset.copy()
    iter_linkset = linkset.copy()
    for link in tqdm(iter_linkset):
        if len(link) == 3:
            continue
        cluster = {}
        layer_num = 1
        cluster["layer_" + str(layer_num)] = [link]
        link['is_linked'] = 1
        cluster, layer_num, number_list, iter_linkset = find_sub_links(cluster, layer_num, number_list, iter_linkset, search_linkset)
        if len(cluster) > 1:            # 只选取包含两次以上link的cluster
            # 添加3个字段，cluster的层数，点数和最晚点的时间-最早点的时间
            node_count = 1              # node number初始为1，因为源节点始终有一个
            time_list = []
            for key in cluster.keys():
                node_count += len(cluster[key])
                for link in cluster[key]:
                    time_list.append(link['source']['createdAt'])
                    for tar in link['target']:
                        time_list.append(tar['createdAt'])

            cluster["layers_count"] = len(cluster)
            cluster["nodes_count"] = node_count
            time_interval_s = sorted(time_list, key=lambda data: get_time(data))
            time_format = "%Y-%m-%dT%H:%M:%SZ"
            time_interval = datetime.strptime(time_interval_s[-1],time_format).__sub__(datetime.strptime(time_interval_s[0], time_format)).total_seconds()
            cluster["cluster_time_interval"] = time_interval

            cluster_list.append(cluster)
    return cluster_list


def find_sub_links(cluster, layer_num, number_list, iter_linkset, search_linkset):
    layer_num += 1
    cluster["layer_" + str(layer_num)] = []
    for i in range(0,len(cluster["layer_" + str(layer_num-1)])):
        for tar in cluster["layer_" + str(layer_num-1)][i]['target']:
            for number in number_list[1:]:
                if number == tar['number']:
                    link = search_linkset[number_list.index(number)]
                    if len(link) == 2:
                        cluster["layer_" + str(layer_num)].append(link)
                        search_linkset[number_list.index(number)]['is_linked'] = 1         # 已经连接过的Link打上is_linked标签
                        iter_linkset[number_list.index(number)]['is_linked'] = 1         # 已经连接过的Link打上is_linked标签
                        break
    if cluster["layer_" + str(layer_num)]:
        cluster, layer_num, number_list, linkset = find_sub_links(cluster, layer_num, number_list, iter_linkset, search_linkset)
    else:
        del cluster["layer_" + str(layer_num)]
    return cluster, layer_num, number_list, iter_linkset

def parse_1_and_N(linkset):
    source_index_list, target_index_list = [], []
    source = []
    for i in tqdm(range(0,len(linkset))):
        target = []
        try:
            index_s = source.index(linkset[i]['source']['number'])
            target_index_list[index_s].append(i)
        except Exception:
            source.append(linkset[i]['source']['number'])
            source_index_list.append(i)
            target.append(i)
            target_index_list.append(target)

    link_1_1, link_1_N = [], []
    for source_index, target_index in zip(source_index_list, target_index_list):
        target_list = []
        for t in target_index:
            target_list.append(linkset[t]['target'])
        dic = {'source': linkset[source_index]['source'] , 'target': target_list}
        if len(target_index) == 1:
            link_1_1.append(dic)
        else:
            link_1_N.append(dic)
    return link_1_1, link_1_N

def detect_dup(links,link):
    repeat = 0
    if link:
        for i in range(len(links) - 1, 0, -1):
            if (link['source']['number'] == links[i]['target']['number'] and link['target']['number'] == links[i]['source']['number']) or \
               (link['source']['number'] == links[i]['source']['number'] and link['target']['number'] == links[i]['target']['number']) :
                repeat = 1  # 该link与之前的link重复
        if repeat == 0:
            links.append(link)
    return links

def parse_bilateral(linkset):
    link_self_bilateral,link_bilateral = [],[]
    count = 0
    for link in tqdm(linkset):
        count += 1
        if link['source']['number'] == link['target']['number']:
            link_self_bilateral = detect_dup(link_self_bilateral,link)
        else:
            for subiter in linkset:
                if subiter['source']['number'] == link['target']['number'] and link['source']['number']==subiter['target']['number']:
                    link_bilateral = detect_dup(link_bilateral,subiter)
    return link_self_bilateral, link_bilateral


def visulize_link_self_bila():
    link_list = []
    for o_r in init.repos_to_get_info:
        owner, name = o_r[0], o_r[1]
        link_self = file_opt.read_json_from_file(init.local_data_filepath+owner+"/"+name+"/link_self_bi.json")
        link_bila = file_opt.read_json_from_file(init.local_data_filepath+owner+"/"+name+"/link_bi.json")
        link_list.append({'repo':owner+"/"+name, 'link_self': link_self,'link_bilateral': link_bila})

    # vis.visualization_multi_self_bila(link_list)

def work(fullrepo):

    owner, name = fullrepo[0], fullrepo[1]
    print("-------------------start " + owner + "/" + name + "---------------------------")
    link_type = file_opt.read_json_from_file(init.local_data_filepath+owner+"/"+name+"/links_type.json")
    link_1_1, link_1_N, link_self_bilateral, link_bilateral, link_cluster = \
        extract_link_mode(link_type,renew,init.local_data_filepath+owner+"/"+name+"/")

    # 查看单个repo的分布
    # vis.visualization_how_1_or_N(link_1_1, link_1_N, repo=owner+'/'+name)
    # vis.visualization_how_self_or_bilateral(link_self_bilateral, link_bilateral, repo=owner+'/'+name)
    vis.visualization_how_cluster(link_cluster, repo=owner+'/'+name)
    # visulize_link_self_bila()       # 查看多个repo链自己和相互链接的统计
    print("-------------------finish " + owner + "/" + name + "---------------------------")
if __name__ == '__main__':
    from concurrent.futures import ThreadPoolExecutor as PoolExecutor
    repolist = init.repos_to_get_info
    with PoolExecutor(max_workers=5) as executor:
        for _ in executor.map(work, repolist):
            pass