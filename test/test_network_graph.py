import pandas as pd
from histcite.network_graph import GraphViz

file_path = 'test/citation_table.xlsx'
citation_table = pd.read_excel(file_path,dtype_backend='pyarrow') # type:ignore
doc_indices = citation_table.sort_values('LCS', ascending=False).index[:50]
G = GraphViz(citation_table)
graph_dot_file = G.generate_dot_file(doc_indices)
assert graph_dot_file[:7] == 'digraph'

graph_node_file = G.generate_graph_node_file()
assert isinstance(graph_node_file,pd.DataFrame)