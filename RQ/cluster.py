### 分析cluster的特征
from utils import file_opt
from prepare import init

def main():
    for o_r in init.repos_to_get_info:
        owner, name = o_r[0], o_r[1]
        print("--------------------handle " + owner + "/" + name + "---------------------------")
        cluster = file_opt.read_json_from_file(init.local_data_filepath + owner + "/" + name + "/"+"link_cluster.json")
        for clust in cluster:
            if clust['cluster_time_interval'] < 100 and clust['nodes_count'] > 18 :
                print(clust["nodes_count"],clust["cluster_time_interval"],clust['layer_1'][0]['source']['number'])
        a=1

if __name__ == '__main__':
    main()