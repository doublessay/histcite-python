# HistCite工具的Python实现

由于原引文分析工具 [HistCite](https://support.clarivate.com/ScientificandAcademicResearch/s/article/HistCite-No-longer-in-active-development-or-officially-supported) 已停止维护，目前国内普遍使用的为国科大某位同学在原程序基础上进行修复的版本 [HistCite Pro](https://zhuanlan.zhihu.com/p/20902898)，仅能在 `Windows` 平台上运行，存在诸多限制。借助 [pandas 2.0](https://pandas.pydata.org/docs/dev/whatsnew/v2.0.0.html) 和可视化工具 [Graphviz](https://graphviz.org)，本工具复刻了原 `HistCite` 的大部分功能，同时拓展了对其他数据源的支持，可以跨平台使用。

最近更新：
- `v0.3.0` 增加了对 `Scopus` 数据库题录数据的支持；
- `v0.2.0` 增加了对 `CSSCI` 数据库题录数据的支持；

核心功能：
- 生成引文网络图；
- 生成统计数据，其中包括文献、作者、机构、文献来源、作者关键词等；  
- 发现不在本地文献集中、但被本地文献集引用较多的文献；

术语说明：
- `GCS`, Global Citation Score， 表示一篇文献在 Web of Science核心合集中的总被引次数；
- `LCS`, Local Citation Score，表示一篇文献在本地论文集中的被引次数；
- `GCR`, Global Cited References，表示一篇文献所有参考文献的数量；
- `LCR`, Local Cited References，表示一篇文献所有本地参考文献的数量；
- `T*`, Total，表示给定作者、机构、期刊等相应分数之和。例如 `TLCS` = 总本地引文数；
- `Recs`， 记录数；
- `Web of Science` 题录数据 [字段说明](https://images.webofknowledge.com/WOKRS5132R4.2/help/zh_CN/WOS/hs_wos_fieldtags.html)；
- 其他来源的题录数据会沿用 `Web of Science` 的字段命名格式；

工具对比：
| 对比项 | histcite-python | histcite pro |
| :-: | :-: | :-: |
| 是否开源 | 是 | 否 |
| 是否跨平台 | 是 | 否，仅限 Windows |
| 是否支持其他数据源 | 是 | 否，仅限 Web of Science |
| 是否提供前端界面 | 否 | 是 |
| 引文网络图 | 矢量图，比较清晰 | 位图，比较粗糙 |

## 快速开始
```console
# 需要 Python3.8 或以上版本
pip install histcite-python
```

## 数据准备
| 数据来源 | 下载说明 |
| :---: | --- |
| `Web of Science` | `核心合集`，格式选择 `Tab delimited file/制表符分隔文件`，导出内容选择 `Full Record and Cited References/全记录与引用的参考文献` 或者是 `Custome selection/自定义选择项`，全选字段。 |
| `CSSCI` | 从 `CSSCI数据库` 正常导出即可。 |
| `Scopus` | 格式选择 `CSV` 文件，导出字段需要额外勾选 `Author keywords` 和 `Include references`，或者直接全选字段。 |
>⚠️ 文件下载之后不要改名(会根据文件名识别有效的题录数据文件)，下载完成后放在一个单独的文件夹内。

## 使用方法
1、使用命令行工具，可用参数如下：
|  | 参数 | 说明 |
| :---: | :---: | --- |
| -f | --folder_path | 下载的题录数据存放的文件夹路径，必须指定 |
| -t | --source_type | 题录数据来源，可选 `wos`、`cssci`、`scopus`，必须指定 |
| -n | --node_num | 引文网络图中包含的节点数量，默认为 `50`，即 `LCS` 最高的 `50` 篇文献 |
| -g | --graph | 是否仅生成图文件，指定该参数表示 `True`，无需传值 |

```console
$ 假设文件夹路径为/Users/.../downloads/dataset，来源为web of science, 引文网络图节点数设置为100
$ histcite -f /Users/.../downloads/dataset -t wos -n 100
```
>注：结果保存在指定的 `folder_path` 下的 `result` 文件夹内，包含 statistics.xlsx, graph.node.xlsx, graph.dot 三个文件，第一个是描述统计表，第二个是引文网络图节点信息表，最后一个为引文网络图的数据文件，可以使用 [Graphviz在线编辑器](http://magjac.com/graphviz-visual-editor/) 或本地的 [Graphviz工具](https://graphviz.org/) 生成引文网络图。具体内容可以参考 [examples文件夹](examples)。 

生成的引文网络图：

<img src="examples/graph.svg">

对应的文献节点信息：

|    | AU            |   PY | SO                                               |   VL |   BP |   LCS |   GCS |
|------------:|:--------------|-----:|:-------------------------------------------------|-----:|-----:|------:|------:|
|          31 | Iyer R        | 1997 | IEEE SIGNAL PROCESSING LETTERS                   |    4 |  221 |     5 |    24 |
|          58 | Iyer RM       | 1999 | IEEE TRANSACTIONS ON SPEECH AND AUDIO PROCESSING |    7 |   30 |    10 |    55 |
|          68 | Iver R        | 1999 | COMPUTER SPEECH AND LANGUAGE                     |   13 |  267 |     7 |    14 |
|          77 | Bellegarda JR | 2000 | IEEE TRANSACTIONS ON SPEECH AND AUDIO PROCESSING |    8 |   76 |     7 |    43 |
|          82 | Bellegarda JR | 2000 | PROCEEDINGS OF THE IEEE                          |   88 | 1279 |    15 |   210 |

2、函数调用，相比命令行工具，函数调用更加灵活，可以自定义更多参数，参考 [demo.ipynb](demo.ipynb)

```python
import os
import pandas as pd
from histcite.process_file import ProcessFile
from histcite.compute_metrics import ComputeMetrics
from histcite.network_graph import GraphViz

# 读取数据，解析引文
folder_path = '/Users/.../downloads/dataset' # 下载的题录数据存放的文件夹路径
source_type = 'wos'
process = ProcessFile(folder_path, source_type)
process.concat_table() # 合并多个文件
process.process_citation() # 识别引文关系
docs_table = process.docs_table
reference_table = process.reference_table

# 基本描述统计
cm = ComputeMetrics(docs_table, reference_table, source_type)
cm.write2excel(os.path.join(folder_path,'result','statistics.xlsx'))

# 生成引文网络图文件
graph = GraphViz(docs_table, source_type)
doc_indices = docs_table.sort_values('LCS', ascending=False).index[:100] # 选取LSC最高的100篇文献
graph_dot_file = graph.generate_dot_file(doc_indices, allow_external_node=False)

# 保存引文网络图文件
with open(os.path.join(folder_path,'result','graph.dot'), 'w') as f:
    f.write(graph_dot_file)

# 保存引文网络图节点文件
graph_node_file = graph.generate_graph_node_file()
graph_node_file.to_excel(os.path.join(folder_path,'result','graph.node.xlsx'),index=False)
```
>注：`generate_dot_file` 函数的 `allow_external_node` 参数表示引文网络节点中是否允许出现 `doc_indices` 之外的节点文献，`doc_indices` 一般为 `LCS` 比较高的文献，这些文献同样会参考低 `LCS` 的文献，或被低 `LCS` 的文献引用，因此如果将 `allow_external_node` 设置为 `True`，引文网络图中将会出现这些低 `LCS` 的文献节点，默认为 `False`。

## 实现细节
|  | Web of Science | CSSCI | Scopus|
| --- | --- | --- | --- |
| 如何识别引文关系 | 如果存在 `DOI`，则优先使用 `DOI` 进行匹配；否则通过 `一作`、`发表年份`、`文献来源`、`开始页` 进行判断  | 通过 `一作 `和 `题名` 进行判断 | 通过 `一作 `和 `题名` 进行判断 |
| 如何去重 | 根据 `UT` 入藏号进行去重 | 根据 `一作` 和 `题名` 字段进行去重 | 根据 `EID` 字段进行去重 |

## Q&A
1、为什么选取 `LSC` 最高的100篇文献，但是引文网络图及图节点文件中的节点数量少于100？  
答：考虑到实用性和美观性，程序会自动忽略没有边的节点。即这些选中的文献没有引用其他选中的文献，或被这些文献引用。

## TODO
- [x] 支持 `CSSCI` 题录数据
- [x] 支持 `Scopus` 题录数据
- [ ] 支持 `PubMed` 题录数据