import pytest
import pandas as pd
from histcite.network_graph import GraphViz

@pytest.mark.skip(reason='This is a function factory')
def test_graph(file_path,source_type):
    def new_func():
        docs_table = pd.read_csv(file_path,dtype_backend='pyarrow')
        doc_indices = docs_table.sort_values('LCS', ascending=False).index[:10]
        G = GraphViz(docs_table,source_type)
        graph_dot_file = G.generate_dot_file(doc_indices)
        return graph_dot_file
    return new_func

def test_wos_graph():
    file_path = 'tests/wos_docs_table.csv'
    graph_dot_file = test_graph(file_path,'wos')()
    assert graph_dot_file[:7] == 'digraph'

def test_cssci_graph():
    file_path = 'tests/cssci_docs_table.csv'
    graph_dot_file = test_graph(file_path,'cssci')()
    assert graph_dot_file[:7] == 'digraph'

def test_scopus_graph():
    file_path = 'tests/scopus_docs_table.csv'
    graph_dot_file = test_graph(file_path,'scopus')()
    assert graph_dot_file[:7] == 'digraph'