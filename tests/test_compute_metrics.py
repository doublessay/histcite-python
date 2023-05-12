import pandas as pd
from histcite.compute_metrics import ComputeMetrics

def test_wos_statistics():
    docs_table = pd.read_csv('tests/wos_docs_table.csv',dtype_backend='pyarrow')
    reference_table = pd.read_csv('tests/wos_reference_table.csv',dtype_backend='pyarrow')

    cm = ComputeMetrics(docs_table,reference_table,'wos')
    author_table = cm._generate_author_table()
    assert isinstance(author_table.index[0],str)
    keywords_table = cm._generate_keywords_table()
    assert isinstance(keywords_table.index[0],str)

def test_cssci_statistics():
    docs_table = pd.read_csv('tests/cssci_docs_table.csv',dtype_backend='pyarrow')
    reference_table = pd.read_csv('tests/cssci_reference_table.csv',dtype_backend='pyarrow')

    cm = ComputeMetrics(docs_table,reference_table,'cssci')
    author_table = cm._generate_author_table()
    assert isinstance(author_table.index[0],str)
    keywords_table = cm._generate_keywords_table()
    assert isinstance(keywords_table.index[0],str)