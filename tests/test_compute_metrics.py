import pytest
import pandas as pd
from histcite.compute_metrics import ComputeMetrics

@pytest.mark.skip(reason='This is a function factory')
def test_statistics(docs_table_path,reference_table_path,source_type):
    def new_func():
        docs_table = pd.read_csv(docs_table_path,dtype_backend='pyarrow')
        reference_table = pd.read_csv(reference_table_path,dtype_backend='pyarrow')

        cm = ComputeMetrics(docs_table,reference_table,source_type)
        author_table = cm._generate_author_table()
        keywords_table = cm._generate_keywords_table()
        return author_table,keywords_table
    return new_func

def test_wos_statistics():
    docs_table_path = 'tests/wos_docs_table.csv'
    reference_table_path = 'tests/wos_reference_table.csv'
    author_table,keywords_table = test_statistics(docs_table_path,reference_table_path,'wos')()
    assert isinstance(author_table.index[0],str)
    assert isinstance(keywords_table.index[0],str)

def test_cssci_statistics():
    docs_table_path = 'tests/cssci_docs_table.csv'
    reference_table_path = 'tests/cssci_reference_table.csv'
    author_table,keywords_table = test_statistics(docs_table_path,reference_table_path,'cssci')()
    assert isinstance(author_table.index[0],str)
    assert isinstance(keywords_table.index[0],str)
 
def test_scopus_statistics():
    docs_table_path = 'tests/scopus_docs_table.csv'
    reference_table_path = 'tests/scopus_reference_table.csv'
    author_table,keywords_table = test_statistics(docs_table_path,reference_table_path,'scopus')()
    assert isinstance(author_table.index[0],str)
    assert isinstance(keywords_table.index[0],str)