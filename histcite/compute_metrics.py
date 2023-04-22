import os
import pandas as pd

class ComputeMetrics:
    """生成统计结果"""

    def __init__(self,citation_table,reference_table):
        self.citation_table = citation_table
        self.reference_table = reference_table

    def __generate_table(self,use_cols:list,col:str,split_char=None)->pd.DataFrame:
        
        df = self.citation_table[use_cols]
        # 如果字段包含多个值，则进行拆分
        if split_char:
            try:
                df = df.dropna(subset=[col])
                df[col] = df[col].str.split(split_char)
            except NotImplementedError:
                df = df.astype({col:'str'})
                df[col] = df[col].str.split(split_char)
            df = df.explode(col)
            df = df.reset_index(drop=True)
        
        if 'LCS' in use_cols:
            grouped_df = df.groupby(col).agg({col: 'count', 'LCS': 'sum', 'TC': 'sum'})
            grouped_df = grouped_df.rename(columns={col: 'Recs', 'LCS': 'TLCS', 'TC': 'TGCS'})
        else:
            grouped_df = df.groupby(col).agg({col: 'count'}).rename(columns={col: 'Recs'})
        return grouped_df.sort_values('Recs', ascending=False)
    
    def _generate_author_table(self):
        use_cols = ['AU','LCS','TC']
        return self.__generate_table(use_cols,'AU','; ')
    
    def _generate_keywords_table(self):
        use_cols = ['DE','LCS','TC']
        return self.__generate_table(use_cols,'DE','; ')
    
    def _generate_institution_table(self):
        use_cols = ['C3','LCS','TC']
        return self.__generate_table(use_cols,'C3','; ')
    
    def _generate_records_table(self):
        """生成文献简表"""
        use_cols = ['AU','TI','SO','LCS','TC','LCR','NR']
        records_table = self.citation_table[use_cols]
        records_table = records_table.rename(columns={'TC':'GCS','NR':'GCR'})
        return records_table
    
    def _generate_journal_table(self):
        use_cols = ['SO','LCS','TC']
        return self.__generate_table(use_cols,'SO')

    def _generate_year_table(self):
        use_cols = ['PY']
        return self.__generate_table(use_cols,'PY')
    
    def _generate_document_type_table(self):
        use_cols = ['DT']
        return self.__generate_table(use_cols,'DT')
   
    def _generate_reference_table(self):
        """生成参考文献表，按照引用次数降序排列，同时标记是否为本地文献"""
        check_cols = ['PY','J9','VL','BP']
        use_cols = self.reference_table.columns.tolist()[:-1]
        reference_table = self.reference_table.groupby(use_cols,as_index=False).size()
        reference_table = reference_table.sort_values(by='size',ascending=False)
        reference_table = reference_table.rename(columns={'size':'Recs'})
        common_table = reference_table.reset_index().merge(self.citation_table[check_cols],on=check_cols)
        reference_table['local'] = 0
        reference_table.loc[common_table['index'],'local'] = 1
        return reference_table
    
    def write2excel(self,save_path):
        """将统计结果写入excel"""
        save_folder_path = os.path.dirname(save_path)
        if not os.path.exists(save_folder_path):
            os.makedirs(save_folder_path)
        with pd.ExcelWriter(save_path) as writer:
            self._generate_records_table().to_excel(writer,sheet_name='Records',index=False)
            self._generate_author_table().to_excel(writer,sheet_name='Authors')
            self._generate_journal_table().to_excel(writer,sheet_name='Journals')
            self._generate_reference_table().to_excel(writer,sheet_name='Cited References',index=False)
            self._generate_keywords_table().to_excel(writer,sheet_name='Keywords')
            self._generate_year_table().to_excel(writer,sheet_name='Years')
            self._generate_document_type_table().to_excel(writer,sheet_name='Document Type')
            self._generate_institution_table().to_excel(writer,sheet_name='Institutions')
