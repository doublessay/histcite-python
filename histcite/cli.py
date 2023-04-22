import os
import argparse
import pandas as pd
from histcite.compute_metrics import ComputeMetrics
from histcite.process_table import ProcessTable
from histcite.network_graph import GraphViz
    
def main():
    parser = argparse.ArgumentParser(description='A Python interface to histcite.')
    parser.add_argument('-f','--folder_path', type=str, help='folder path of the downloaded files')
    parser.add_argument('-n','--node_num', type=int, default=50, help='node number in the citation network graph')
    parser.add_argument('-g','--graph', action="store_true", help='generate graph file only')
    args = parser.parse_args()

    # 将结果存放在用户指定的 folder_path 下的result文件夹中
    output_path = os.path.join(args.folder_path,'result')
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    process = ProcessTable(args.folder_path)
    concated_table = process.concat_table()
    reference_table = process.generate_reference_table(concated_table['CR'])
    citation_table = process.process_citation(reference_table)

    if not args.graph:
        cm = ComputeMetrics(citation_table, reference_table)
        cm_output_path = os.path.join(output_path,'statistics.xlsx')
        cm.write2excel(cm_output_path)

    doc_indices = citation_table.sort_values('LCS', ascending=False).index[:args.node_num]
    graph = GraphViz(citation_table)
    
    # 生成图文件
    graph_dot_file = graph.generate_dot_file(doc_indices)
    graph_dot_path = os.path.join(output_path,'graph.dot')
    with open(graph_dot_path,'w') as f:
        f.write(graph_dot_file)

    # 生成节点文件
    graph_node_file = graph.generate_graph_node_file()
    graph_node_file.to_excel(os.path.join(output_path,'graph.node.xlsx'),index=False)