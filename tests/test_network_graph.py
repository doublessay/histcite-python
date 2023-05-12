import pandas as pd
from histcite.network_graph import GraphViz

def test_wos_graph():
    file_path = 'tests/wos_docs_table.csv'
    docs_table = pd.read_csv(file_path,dtype_backend='pyarrow')
    doc_indices = docs_table.sort_values('LCS', ascending=False).index[:50]
    G = GraphViz(docs_table,'wos')
    graph_dot_file = G.generate_dot_file(doc_indices)
    assert graph_dot_file[:7] == 'digraph'

def test_cssci_graph():
    file_path = 'tests/cssci_docs_table.csv'
    docs_table = pd.read_csv(file_path,dtype_backend='pyarrow')
    doc_indices = docs_table.sort_values('LCS', ascending=False).index[:50]
    G = GraphViz(docs_table,'cssci')
    graph_dot_file = G.generate_dot_file(doc_indices)
    assert graph_dot_file[:7] == 'digraph'