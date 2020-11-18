# pawQL
使用graphQL获取github仓库中issues和pullRequests的关系。  
对这些关系进行分析。  

## 获取数据
- 使用graphQL获取数据，query写在了  `prepare/queries`中，有多种情况，区分了各个情况使用的query。
- 运行`/prepare/prepare_response.py`会在相应的文件夹中生成各个仓库的文件夹，存储`request_pullRequests.json`和`request_issues.json`  
    - 使用graphQL获取数据经常会被拒绝，要多准备一些token，token列表存放在`/data/token_list.txt`中，git不会上传token_list.txt，所以新项目要自己创建这个文件，放入自己的token
   
## 数据分析
- 数据预处理：在`/prepare/preprocess.py`中完成，主要是去除了body中的引用和代码
- 可视化：在`utils/visualization.py`中完成，根据需求使用不同的函数。这个部分现在还有点乱（2020年11月18日）
### RQ123.py
对应RQ1，RQ2和RQ3
- RQ1：区分link的类型，pullRequest to pullRequest, pullRequest to issue, issue to pullRequest, issue to issue.
- RQ2：标识出link出现的位置, title, body, comment
- RQ3: 统计link的时间间隔， create time interval, link time interval
运行`RQ/RQ123.py`即可在对应的文件夹中生成处理后的数据。
### RQ4.py
- 1to1：一对一的链接
- 1toN：一对多的链接
- N_step_circle：多步成环
运行`RQ/RQ4.py`即可在对应的文件夹中生成处理后的数据。
### RQ5.py
研究同一个link被提出了多少次，有几个author提出这样的link。  
目前已经停止这个研究了，没有找到研究的意义。
