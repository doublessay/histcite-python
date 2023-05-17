import os
import argparse
from histcite.compute_metrics import ComputeMetrics
from histcite.process_file import ProcessFile
from histcite.network_graph import GraphViz
    
def main():
    parser = argparse.ArgumentParser(description='A Python interface to histcite.')
    parser.add_argument('-f','--folder_path', type=str, required=True, help='folder path of the downloaded files')
    parser.add_argument('-t','--source_type', type=str, required=True, choices=['wos','cssci','scopus'], help='source type of the downloaded files')
    parser.add_argument('-n','--node_num', type=int, default=50, help='node number in the citation network graph')
    parser.add_argument('-g','--graph', action="store_true", help='generate graph file only')
    args = parser.parse_args()

    # 将结果存放在用户指定的folder_path下的result文件夹中
    output_path = os.path.join(args.folder_path,'result')
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    process = ProcessFile(args.folder_path, args.source_type)
    process.concat_table()
    process.process_citation()
    docs_table = process.docs_table
    reference_table = process.reference_table

    if not args.graph:
        cm = ComputeMetrics(docs_table, reference_table, args.source_type)
        cm_output_path = os.path.join(output_path,'statistics.xlsx')
        cm.write2excel(cm_output_path)

    doc_indices = docs_table.sort_values('LCS', ascending=False).index[:args.node_num]
    graph = GraphViz(docs_table,args.source_type)
    
    # 生成图文件
    graph_dot_file = graph.generate_dot_file(doc_indices)
    graph_dot_path = os.path.join(output_path,'graph.dot')
    with open(graph_dot_path,'w') as f:
        f.write(graph_dot_file)

    # 生成图节点文件
    graph._export_graph_node_file(os.path.join(output_path,'graph.node.xlsx'))