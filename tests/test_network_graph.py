import pandas as pd
from histcite.network_graph import GraphViz

file_path = 'tests/docs_table.xlsx'
docs_table = pd.read_excel(file_path,dtype_backend='pyarrow') # type:ignore
doc_indices = docs_table.sort_values('LCS', ascending=False).index[:50]
G = GraphViz(docs_table)
graph_dot_file = G.generate_dot_file(doc_indices)
assert graph_dot_file[:7] == 'digraph'