from utils import file_opt
import init
from utils import visualization as vis

renew = 0

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

def parse_link_cluster(link_1_1,link_1_N):
    source_number_11_list = extract_number_list(link_1_1)
    source_number_1N_list = extract_number_list(link_1_N)
    number_list = source_number_11_list + source_number_1N_list
    linkset = link_1_1+link_1_N
    cluster_list = []
    while linkset:
        cluster = {}
        layer_num = 1
        cluster["layer_" + str(layer_num)] = [linkset[0]]
        del linkset[0]
        del number_list[0]
        cluster, layer_num, number_list, linkset = find_sub_links(cluster, layer_num, number_list, linkset)
        cluster_list.append(cluster)
    return cluster_list


def find_sub_links(cluster, layer_num, number_list, linkset):
    # print(layer_num)
    layer_num += 1
    cluster["layer_" + str(layer_num)] = []
    for i in range(0,len(cluster["layer_" + str(layer_num-1)])):
        for tar in cluster["layer_" + str(layer_num-1)][i]['target']:
            already_used_index = []
            for number in number_list[1:]:
                if number == tar['number']:
                    cluster["layer_" + str(layer_num)].append(linkset[number_list.index(number)])
                    already_used_index.append(number_list.index(number))
                    break

            for index in already_used_index:
                del linkset[index]
                del number_list[index]
    if cluster["layer_" + str(layer_num)]:
        cluster, layer_num, number_list, linkset = find_sub_links(cluster, layer_num, number_list, linkset)
    else:
        del cluster["layer_" + str(layer_num)]
    return cluster, layer_num, number_list, linkset

def parse_1_and_N(linkset):
    source_index_list, target_index_list = [], []
    source = []
    for i in range(0,len(linkset)):
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
    for link in linkset:
        count += 1
        # print(count)
        if link['sourc e']['number'] == link['target']['number']:
            link_self_bilateral = detect_dup(link_self_bilateral,link)
        else:
            for subiter in linkset:
                if subiter['source']['number'] == link['target']['number'] and link['source']['number']==subiter['target']['number']:
                    link_bilateral = detect_dup(link_bilateral,subiter)
    return link_self_bilateral, link_bilateral

def work():
    for o_r in init.repos_to_get_info:
        owner, repo = o_r[0], o_r[1]
        print("--------------------handle " + owner + "/" + repo + "---------------------------")
        link_type = file_opt.read_json_from_file(init.local_data_filepath+owner+"/"+repo+"/links_type.json")
        link_1_1, link_1_N, link_self_bilateral, link_bilateral, link_cluster = \
            extract_link_mode(link_type,renew,init.local_data_filepath+owner+"/"+repo+"/")
    return link_1_1, link_1_N, link_self_bilateral, link_bilateral, link_cluster

if __name__ == '__main__':
    link_1_1, link_1_N, link_self_bilateral, link_bilateral, link_cluster = work()
    vis.visualization_how_1_or_N(link_1_1, link_1_N)
    vis.visualization_how_self_or_bilateral(link_self_bilateral, link_bilateral)
    vis.visualization_how_cluster(link_cluster)