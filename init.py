repo_list_file = "../data/repository_list.txt"
local_data_filepath = "D:/analyse_link/"

# 获取仓库列表
with open(repo_list_file, 'r') as f:
    repo_list = f.readlines()
    repos_to_get_info = []
    for item in repo_list:
        repos_to_get_info.append([item.strip().split("/")[0], item.strip().split("/")[1]])