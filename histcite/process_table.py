import os
import pandas as pd
from histcite.parse_citation import ParseCitation

class ProcessTable:
    """处理表单数据"""

    def __init__(self,folder_path:str):
        """
        folder_path: 文件夹路径
        """
        self.folder_path = folder_path
        self.check_cols = ['PY', 'J9','VL','BP']
        self.file_name_list = [i for i in os.listdir(folder_path) if i[:4]=='save']
        
    def _read_table(self,file_name:str)->pd.DataFrame:
        """读取表单，返回dataframe"""

        use_cols = ['AU','TI','SO','DT','CR','DE','C3','NR','TC','Z9','J9','PY','VL','BP','DI','UT']
        file_path = os.path.join(self.folder_path,file_name)
        df = pd.read_csv(
            file_path,sep='\t',
            header=0,
            on_bad_lines='skip',
            usecols=use_cols,
            dtype_backend="pyarrow") # type: ignore
                              
        return df
    
    def concat_table(self):
        """合并多个dataframe"""

        docs_table = pd.concat([self._read_table(file_name) for file_name in self.file_name_list],ignore_index=True,copy=False)
        # 根据入藏号删除重复数据，一般不会有重复数据
        docs_table.drop_duplicates(subset='UT',ignore_index=True,inplace=True)

        # 转换数据类型
        docs_table['BP'] = docs_table['BP'].apply(pd.to_numeric,errors='coerce')
        docs_table['VL'] = docs_table['VL'].apply(pd.to_numeric,errors='coerce')
        docs_table = docs_table.astype({'BP':'int64[pyarrow]', 'VL':'int64[pyarrow]'})
        
        # 提取一作
        # docs_table['AU'] = docs_table['AU'].apply(lambda x:self.extract_first_author(x))
        
        # 按照年份进行排序
        docs_table = docs_table.sort_values(by='PY',ignore_index=True)
        docs_table.insert(0,'doc_index',docs_table.index)
        self.docs_table = docs_table
        return docs_table
    
    @staticmethod
    def generate_reference_table(cr_series:pd.Series):
        """生成参考文献表格"""
        parsed_cr_cells = [ParseCitation(doc_index,cell).parse_cr_cell() for doc_index,cell in cr_series.items()]
        reference_table = pd.concat([pd.DataFrame.from_dict(cell) for cell in parsed_cr_cells if cell],ignore_index=True)
        reference_table = reference_table.astype({'PY':'int64[pyarrow]', 'VL':'int64[pyarrow]', 'BP':'int64[pyarrow]'})
        return reference_table

    def __recognize_reference(self,row_index:int,row_year:int,row_references:pd.DataFrame):
        """识别本地参考文献
        row_index: 文献索引
        row_year: 文献年份
        row_references: 文献参考文献
        """
        docs_table_cols = ['doc_index']+self.check_cols
        local_ref_list = []
        child_docs_table = self.docs_table[self.docs_table['PY'] <= row_year]
        child_citation_table = row_references

        # 存在DOI
        child_docs_table_doi = child_docs_table[child_docs_table['DI'].notna()]['DI']
        child_citation_table_doi = child_citation_table[child_citation_table['DI'].notna()]['DI']
        local_ref_list.extend(child_docs_table_doi[child_docs_table_doi.isin(child_citation_table_doi)].index.tolist())
        
        # 不存在DOI
        child_docs_table_left = child_docs_table[child_docs_table['DI'].isna()][docs_table_cols]
        child_citation_table_left = child_citation_table[child_citation_table['DI'].isna()][self.check_cols]
        common_table = pd.merge(child_docs_table_left,child_citation_table_left,on=self.check_cols)
        if common_table.shape[0]>0:
            common_table = common_table.drop_duplicates(subset='doc_index',ignore_index=True)
            local_ref_list.extend(common_table['doc_index'].tolist())
            try:
                local_ref_list.remove(row_index)
            except ValueError:
                pass
            if local_ref_list:
                return ';'.join([str(i) for i in local_ref_list])
    
    @staticmethod
    def __reference2citation(reference_field:pd.Series):
        """参考文献转换到引文"""
        citation_field = [[] for i in range(len(reference_field))]
        for index, ref in reference_field.items():
            if ref:
                ref_list = ref.split(';')
                for i in ref_list:
                    citation_field[int(i)].append(index)
        citation_field = [';'.join([str(j) for j in i]) if i else None for i in citation_field]
        return citation_field
    
    def process_citation(self,reference_table:pd.DataFrame)->pd.DataFrame:
        """处理引文，生成主表"""

        self.docs_table['reference'] = self.docs_table.apply(lambda row:self.__recognize_reference(row.name,row['PY'],reference_table[reference_table['doc_index']==row.name]),axis=1) # type: ignore
        self.docs_table['citation'] = self.__reference2citation(self.docs_table['reference'])
        self.docs_table['LCR'] = self.docs_table['reference'].apply(lambda x: len(x.split(';')) if x else 0)
        self.docs_table['LCS'] = self.docs_table['citation'].apply(lambda x: len(x.split(';')) if x else 0)
        return self.docs_table