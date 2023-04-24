import pandas as pd
from histcite.compute_metrics import ComputeMetrics

docs_table = pd.read_excel('tests/docs_table.xlsx',dtype_backend='pyarrow') # type:ignore
reference_table = pd.read_excel('tests/reference_table.xlsx',dtype_backend='pyarrow') # type:ignore

cm = ComputeMetrics(docs_table,reference_table)
author_table = cm._generate_author_table()
assert isinstance(author_table.index[0],str)

keywords_table = cm._generate_keywords_table()
assert isinstance(keywords_table.index[0],str)