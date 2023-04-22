import pandas as pd
from histcite.network_graph import GraphViz

file_path = 'test/citation_table.xlsx'
citation_table = pd.read_excel(file_path,dtype_backend='pyarrow') # type:ignore
doc_indices = citation_table.sort_values('LCS', ascending=False).index[:50]
G = GraphViz(citation_table)
dot_text = G.generate_dot_text(doc_indices)

assert dot_text[:7] == 'digraph'