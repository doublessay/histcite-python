import pandas as pd
from histcite.compute_metrics import ComputeMetrics

citation_table = pd.read_excel('test/citation_table.xlsx',dtype_backend='pyarrow') # type:ignore
reference_table = pd.read_excel('test/reference_table.xlsx',dtype_backend='pyarrow') # type:ignore

cm = ComputeMetrics(citation_table,reference_table)
author_table = cm._generate_author_table()
assert author_table.index[0]=='Ney, H'
assert author_table.iloc[0,0] == 21
assert author_table.iloc[0,1] == 41

keywords_table = cm._generate_keywords_table()
assert keywords_table.index[0] == 'speech recognition'
assert keywords_table.iloc[0,0] == 108
assert keywords_table.iloc[0,1] == 153

