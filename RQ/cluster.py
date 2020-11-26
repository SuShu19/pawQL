### 分析cluster的特征
from utils import file_opt
from prepare import init

def main():
    for o_r in init.repos_to_get_info:
        owner, name = o_r[0], o_r[1]
        print("--------------------handle " + owner + "/" + name + "---------------------------")
        clusters = file_opt.read_json_from_file(init.local_data_filepath + owner + "/" + name + "/"+"link_cluster.json")
        clusters_files = create_file_list(clusters)
        divide_module(clusters_files)

def divide_module(clusters_files):
    clusters_module = []
    for file_list in clusters_files:
        module = []
        for path in file_list:
            if path.find("/") >= 0:
                module.append(path.split("/")[0]+"/"+path.split("/")[1])
            else:
                module.append(path)
        clusters_module.append(module)
    return None


def create_file_list(clusters):
    clusters_files = []
    for cluster in clusters:
        each_cluster_files = []
        for layer in cluster.keys():
            if type(cluster[layer]) == list:
                for link in cluster[layer]:
                    if type(link["source"]["files"]) == list:
                        each_cluster_files += link["source"]["files"]   # todo 修改了linktype的结果之后要换成files
                    else:
                        each_cluster_files += link["source"]["file_count"]
                    for tar in link["target"]:
                        if type(tar["file_count"]) == list:
                            each_cluster_files += tar["file_count"]     # todo 修改了linktype的结果之后要换成files
                        else:
                            each_cluster_files += tar["files"]
        clusters_files.append(each_cluster_files)
    return clusters_files


if __name__ == '__main__':
    main()