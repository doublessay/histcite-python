import argparse
import os
from histcite.compute_metrics import ComputeMetrics
from histcite.process_table import ProcessTable
from histcite.network_graph import GraphViz

def generate_file_path(output_path:str, file_name:str):
    if output_path:
        return os.path.join(output_path,file_name)
    else:
        return file_name
    
def main():
    parser = argparse.ArgumentParser(description='A Python interface to histcite.')
    parser.add_argument('-f','--folder_path', type=str, help='下载的题录数据存放的文件夹路径')
    # parser.add_argument('-o','--output_path', type=str, default=None, help='结果保存路径，默认为当前目录')
    parser.add_argument('-g','--graph', type=str, default='false', help='是否仅生成图文件，默认为false')
    parser.add_argument('-n','--node_num', type=int, default=50, help='生成图文件的节点数量，默认为50')
    args = parser.parse_args()

    # 将结果存放在用户指定的 folder_path 下的result文件夹中
    output_path = os.path.join(args.folder_path,'result')
    process = ProcessTable(args.folder_path)
    concated_table = process.concat_table()
    reference_table = process.generate_reference_table(concated_table['CR'])
    citation_table = process.process_citation(reference_table)

    if args.graph == 'false':
        cm = ComputeMetrics(citation_table, reference_table)
        cm_output_path = generate_file_path(output_path,'statistics.xlsx')
        cm.write2excel(cm_output_path)

    doc_indices = citation_table.sort_values('LCS', ascending=False).index[:args.node_num]
    graph = GraphViz(citation_table).generate_dot_text(doc_indices)
    graph_output_path = generate_file_path(output_path,'graph.dot')
    with open(graph_output_path,'w') as f:
        f.write(graph)