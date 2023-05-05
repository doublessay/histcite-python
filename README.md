# HistCite工具的Python实现

由于原引文分析工具 [HistCite](https://support.clarivate.com/ScientificandAcademicResearch/s/article/HistCite-No-longer-in-active-development-or-officially-supported) 已停止维护，目前国内普遍使用的为中科大某位同学在原程序基础上进行修复的版本 [HistCite Pro](https://zhuanlan.zhihu.com/p/20902898)，仅能在 `Windows` 平台上运行，存在诸多限制。借助 [pandas 2.0](https://pandas.pydata.org/docs/dev/whatsnew/v2.0.0.html) 和可视化工具 [Graphviz](https://graphviz.org)，本工具复刻了原 `HistCite` 的大部分功能，并且可以跨平台使用。

核心功能：
- 生成引文网络图；
- 生成包含文献、作者、机构、期刊、关键词等分析单元的引文统计数据；  

## 术语说明
- `GCS`, Global Citation Score， 表示一篇文献在 Web of Science核心合集中的总被引次数；
- `LCS`, Local Citation Score，表示一篇文献在本地论文集中的被引次数；
- `GCR`, Global Cited References，表示一篇文献所有参考文献的数量；
- `LCR`, Local Cited References，表示一篇文献所有本地参考文献的数量；
- `T*`, Total，表示给定作者、机构、期刊等相应分数之和。例如`TLCS` = 总本地引文分数；
- `Recs`， 记录数；
- Web of science题录数据 [字段说明](https://images.webofknowledge.com/WOKRS5132R4.2/help/zh_CN/WOS/hs_wos_fieldtags.html)；

## 快速开始
> 适用于本工具的数据集，来源Web of Science核心合集，<b> Tab delimited file/制表符分隔文件</b> 格式，导出内容选择 <b>Full Record and Cited References/全记录与引用的参考文献</b> 或者是 <b>Custome selection/自定义选择项</b>，全选字段，下载之后不要修改文件名，放在某个文件夹内；  
```console
# 需要 Python3.8 或以上版本
pip install histcite-python
```

## 使用方法
1、使用命令行工具，可用参数如下：
|  | 参数 | 说明 |
| :---: | :---: | --- |
| -f | --folder_path | 下载的题录数据存放的文件夹路径，必须指定 |
| -n | --node_num | 引文网络图中包含的节点数量，默认为 `50`，即 `LCS` 最高的 `50` 篇文献 |
| -g | --graph | 是否仅生成图文件，指定该参数表示 `True`, 无需传值 |

```console
$ 假设下载的wos文件夹路径为 /Users/.../downloads/dataset，引文网络图包含的节点数设置为 100
$ histcite -f /Users/.../downloads/dataset -n 100
```

> 结果保存在指定的 `folder_path` 下的 `result` 文件夹内，包含 `statistics.xlsx`, `graph.node.xlsx`, `graph.dot` 三个文件，第一个是描述统计表，第二个是引文网络图节点信息表，最后一个为引文网络图的数据文件，可以使用 [Graphviz在线编辑器](http://magjac.com/graphviz-visual-editor/) 或本地的 [Graphviz工具](https://graphviz.org/) 生成引文网络图。具体文件内容可以参考 [examples文件夹](examples)。 

生成的引文网络图：

<img src="examples/graph.svg">

对应的文献节点信息：

|  |      AU       |  PY  | SO                                               |  VL  |  BP  |
| :-------: | :-----------: | :--: | :----------------------------------------------- | :--: | :--: |
|    31     |    Iyer R     | 1997 | IEEE SIGNAL PROCESSING LETTERS                   |  4   | 221  |
|    58     |    Iyer RM    | 1999 | IEEE TRANSACTIONS ON SPEECH AND AUDIO PROCESSING |  7   |  30  |
|    68     |    Iver R     | 1999 | COMPUTER SPEECH AND LANGUAGE                     |  13  | 267  |
|    77     | Bellegarda JR | 2000 | IEEE TRANSACTIONS ON SPEECH AND AUDIO PROCESSING |  8   |  76  |
|    82     | Bellegarda JR | 2000 | PROCEEDINGS OF THE IEEE                          |  88  | 1279 |
|    ...    |               |      |                                                  |      |      |

2、函数调用，相比命令行工具，函数调用更加灵活，可以自定义更多参数，参考 [demo.ipynb](demo.ipynb)

```python
import os
import pandas as pd
from histcite.process_table import ParseTable
from histcite.compute_metrics import ComputeMetrics
from histcite.network_graph import Graphviz

# 读取数据，解析引文
folder_path = '/Users/.../downloads/dataset' # 下载的题录数据存放的文件夹路径
process = ProcessTable(folder_path)
process.concat_table() # 合并多个文件
process.process_citation() # 识别引文关系
docs_table = process.docs_table
reference_table = process.reference_table

# 基本描述统计
cm = ComputeMetrics(docs_table, reference_table)
cm.write2excel(os.path.join(folder_path,'result','statistics.xlsx'))

# 生成引文网络图文件
graph = Graphviz(docs_table)
doc_indices = docs_table.sort_values('LCS', ascending=False).index[:100] # 选取LSC最高的100篇文献
graph_dot_file = graph.generate_dot_file(doc_indices, allow_external_node=False)

# 保存引文网络图文件
with open(os.path.join(folder_path,'result','graph.dot'), 'w') as f:
    f.write(dot_text)

# 保存引文网络图节点文件
graph_node_file = graph.generate_graph_node_file()
graph_node_file.to_excel(os.path.join(folder_path,'result','graph.node.xlsx'),index=False)
```
> 注：`generate_dot_file` 函数的 `allow_external_node` 参数表示引文网络节点中是否允许出现 `doc_indices` 之外的节点文献，`doc_indices` 一般为 `LCS` 比较高的文献，这些文献同样会参考低 `LCS` 的文献，或被低 `LCS` 的文献引用，因此如果将 `allow_external_node` 设置为 `True`, 图文件中将会出现这些低 `LCS` 的文献节点，默认为 `False`。

## 工具对比：
| 对比项 | [histcite-python](https://github.com/doublessay/histcite-python) | [histcite pro](https://zhuanlan.zhihu.com/p/20902898) |
| :-: | :-: | :-: |
| 是否跨平台 | 是 | 否，仅限 `Windows` |
| 是否开源 | 是 | 否 |
| 是否提供前端界面 | 否 | 是 |
| 引文网络图 | 矢量图，比较细腻 | 位图，比较粗糙 |
| 性能 | ... | |

## Q&A
1、如何识别引文关系？  
每条文献元数据都包含 `CR` 字段，表示该文献的参考文献集合。发表时间等于或早于当前文献的其他文献为候选文献，如果这些候选文献存在 `DOI` 信息，则判断 `DOI` 是否在参考文献集合的 `DOI` 列表中；如果不存在 `DOI` 信息，则判断 `第一作者`、`发表年份`、`期刊名称`、`期号` 四个字段信息是否与参考文献集合的某条记录一致，一致则判断为引用关系。  

## TODO
- [ ] 支持 `scopus` 题录数据
- [ ] 构建 `GUI` 页面
