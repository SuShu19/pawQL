from prepare import init
from utils import file_opt
import random

# sample_size = 500  # confidence_level = 90% margin error = 3.665%
# sample_size = 300  # confidence_level = 90% margin error = 4.733%
sample_size = 10  # 补充

def read_repos_data(file_name):
    repo_list = init.repo_list
    RQ_list = []
    for repo in repo_list:
        data = file_opt.read_json_from_file(init.local_data_filepath+repo.strip()+"/"+file_name)
        RQ_list += data
    return RQ_list

def random_sample(all_link):
    sample = random.sample(all_link,sample_size)
    file_opt.save_json_to_file("../card_sorting/sample_"+str(sample_size)+"_supply2.json",sample)
    return

if __name__ == '__main__':
    # 对论文中RQ1，2，3，4的结果进行汇总
    all_link = read_repos_data("links_type.json")
    random_sample(all_link)
    # sorting_result = file_opt.read_json_from_file(init.local_data_filepath+"sample_card_sorted.json")