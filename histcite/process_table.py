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
   
    @staticmethod
    def __extract_first_author(au_cell:str):
        """提取一作"""
        return au_cell.split(';',1)[0].replace(',','')
    
    def concat_table(self):
        """合并多个dataframe"""
        if len(self.file_name_list)>1:
            docs_table = pd.concat([self._read_table(file_name) for file_name in self.file_name_list],ignore_index=True,copy=False)
        elif len(self.file_name_list)==1:
            docs_table = self._read_table(self.file_name_list[0])
        else:
            raise FileNotFoundError('No valid file in the folder')
        
        # 根据入藏号删除重复数据，一般不会有重复数据
        docs_table.drop_duplicates(subset='UT',ignore_index=True,inplace=True)

        # 转换数据类型
        docs_table['BP'] = docs_table['BP'].apply(pd.to_numeric,errors='coerce')
        docs_table['VL'] = docs_table['VL'].apply(pd.to_numeric,errors='coerce')
        docs_table = docs_table.astype({'BP':'int64[pyarrow]', 'VL':'int64[pyarrow]'})
        
        # 提取一作
        first_au = docs_table['AU'].apply(lambda x:self.__extract_first_author(x))
        docs_table.insert(1,'first_AU',first_au)
        
        # 按照年份进行排序
        docs_table = docs_table.sort_values(by='PY',ignore_index=True)
        docs_table.insert(0,'doc_index',docs_table.index)
        self.docs_table = docs_table
        return docs_table
    
    def __generate_reference_table(self,cr_series:pd.Series):
        """生成参考文献表格"""
        parsed_cr_cells = [ParseCitation(doc_index,cell).parse_cr_cell() for doc_index,cell in cr_series.items()]
        reference_table = pd.concat([pd.DataFrame.from_dict(cell) for cell in parsed_cr_cells if cell],ignore_index=True)
        reference_table = reference_table.astype({'PY':'int64[pyarrow]', 'VL':'int64[pyarrow]', 'BP':'int64[pyarrow]'})
        reference_table.rename(columns={'AU':'first_AU'},inplace=True)
        self.reference_table = reference_table
    
    def __recognize_reference(self,row_index,merge_startegy=False)->list:
        """识别一篇文献的本地参考文献"""
        local_ref_list = []
        child_reference_table = self.reference_table[self.reference_table['doc_index']==row_index]
            
        # 存在DOI
        child_reference_table_doi = child_reference_table[child_reference_table['DI'].notna()]['DI']
        child_docs_table_doi = self.docs_table[self.docs_table['DI'].notna()]['DI']
        local_ref_list.extend(child_docs_table_doi[child_docs_table_doi.isin(child_reference_table_doi)].index.tolist())
        
        # 不存在DOI
        compare_cols = ['first_AU','PY','J9','BP']
        child_reference_table_left = child_reference_table[child_reference_table['DI'].isna()].dropna(subset=compare_cols)
        child_reference_py = child_reference_table_left['PY']
        child_reference_bp = child_reference_table_left['BP']

        # 年份符合，页码符合，doi为空
        child_docs_table_left = self.docs_table[(self.docs_table['PY'].isin(child_reference_py))&(self.docs_table['BP'].isin(child_reference_bp)&self.docs_table['DI'].isna())].dropna(subset=compare_cols)
        
        if merge_startegy:
            common_table = child_docs_table_left[['doc_index']+compare_cols].merge(child_reference_table_left)
            if common_table.shape[0]>0:
                common_table = common_table.drop_duplicates(subset='doc_index',ignore_index=True)
                local_ref_list.extend(common_table['doc_index'].tolist())
          
        else:
            for idx,row_data in child_docs_table_left.iterrows():
                for _,child_reference in child_reference_table_left.iterrows():
                    if all(row_data[col]==child_reference[col] for col in compare_cols):
                        local_ref_list.append(idx)
        
        return local_ref_list
    
    @staticmethod
    def __reference2citation(reference_field:pd.Series)->pd.Series:
        """参考文献转换到引文"""
        citation_field = pd.Series([[] for i in range(len(reference_field))])
        for doc_index, ref_list in reference_field.items():
            if ref_list:
                for ref_index in ref_list:
                    citation_field[ref_index].append(doc_index)
        return citation_field
    
    def process_citation(self):
        """处理引文"""
        self.__generate_reference_table(self.docs_table['CR'])
        reference_field = self.docs_table.apply(lambda row:self.__recognize_reference(row.name),axis=1)
        citation_field = self.__reference2citation(reference_field)

        lcr_field = reference_field.apply(len)
        lcs_field = citation_field.apply(len)
        self.docs_table['reference'] = [';'.join([str(j) for j in i]) if i else None for i in reference_field]
        self.docs_table['citation'] = [';'.join([str(j) for j in i]) if i else None for i in citation_field]
        self.docs_table['LCR'] = lcr_field
        self.docs_table['LCS'] = lcs_field