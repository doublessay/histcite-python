import os
import pandas as pd

class ComputeMetrics:
    """生成统计结果"""

    def __init__(self,docs_table,reference_table,source_type:str):
        self.docs_table = docs_table
        self.reference_table = reference_table
        self.source_type = source_type

    def __generate_table(self,use_cols:list,col:str,split_char=None,str_lower=False)->pd.DataFrame:
        df = self.docs_table[use_cols]
        
        # 如果字段包含多个值，则进行拆分
        if split_char:
            df = df.dropna(subset=[col])
            df = df.astype({col:'str'})
            if str_lower:
                col_str_lower = df[col].str.lower()
                df[col] = col_str_lower.str.split(split_char)
            else:
                df[col] = df[col].str.split(split_char)
                
            df = df.explode(col)
            df = df.reset_index(drop=True)
        
        if 'LCS' in use_cols and 'TC' in use_cols:
            grouped_df = df.groupby(col).agg({col: 'count', 'LCS': 'sum', 'TC': 'sum'})
            grouped_df = grouped_df.rename(columns={col: 'Recs', 'LCS': 'TLCS', 'TC': 'TGCS'})
        elif 'LCS' in use_cols and 'TC' not in use_cols:
            grouped_df = df.groupby(col).agg({col: 'count', 'LCS': 'sum'})
            grouped_df.rename(columns={col: 'Recs', 'LCS': 'TLCS'}, inplace=True)
        elif 'LCS' not in use_cols and 'TC' not in use_cols:
            grouped_df = df.groupby(col).agg({col: 'count'}).rename(columns={col: 'Recs'})
        else:
            raise ValueError('Invalid columns list')

        if col == 'Author full names':
            grouped_df.index = grouped_df.index.str.replace(r'\(\d+\)','',regex=True)
        return grouped_df.sort_values('Recs', ascending=False)

    def _generate_author_table(self):
        if self.source_type == 'wos':
            use_cols = ['AU','LCS','TC']
        elif self.source_type == 'cssci':
            use_cols = ['AU','LCS']
        elif self.source_type == 'scopus':
            use_cols = ['Author full names','LCS','TC']
        else:
            raise ValueError('Invalid source type')
        return self.__generate_table(use_cols,use_cols[0],'; ')
    
    def _generate_keywords_table(self):
        if self.source_type in ['wos','scopus']:
            use_cols = ['DE','LCS','TC']
        elif self.source_type == 'cssci':
            use_cols = ['DE','LCS']
        else:
            raise ValueError('Invalid source type')
        return self.__generate_table(use_cols,'DE','; ',True)
    
    def _generate_institution_table(self):
        if self.source_type in ['wos','scopus']:
            use_cols = ['C3','LCS','TC']
        elif self.source_type == 'cssci':
            use_cols = ['C3','LCS']
        else:
            raise ValueError('Invalid source type')
        return self.__generate_table(use_cols,'C3','; ')
    
    def _generate_records_table(self):
        """生成文献简表"""
        if self.source_type in ['wos','scopus']:
            use_cols = ['AU','TI','SO','PY','LCS','TC','LCR','NR','source file']
        elif self.source_type == 'cssci':
            use_cols = ['AU','TI','SO','PY','LCS','LCR','NR','source file']
        else:
            raise ValueError('Invalid source type')
        records_table = self.docs_table[use_cols]
        if self.source_type in ['wos','scopus']:
            records_table = records_table.rename(columns={'TC':'GCS','NR':'GCR'})
        return records_table
    
    def _generate_journal_table(self):
        if self.source_type in ['wos','scopus']:
            use_cols = ['SO','LCS','TC']
        elif self.source_type == 'cssci':
            use_cols = ['SO','LCS']
        else:
            raise ValueError('Invalid source type')
        return self.__generate_table(use_cols,'SO')

    def _generate_year_table(self):
        use_cols = ['PY']
        return self.__generate_table(use_cols,'PY')
    
    def _generate_document_type_table(self):
        use_cols = ['DT']
        return self.__generate_table(use_cols,'DT')
   
    def _generate_reference_table(self):
        """生成参考文献表，按照引用次数降序排列，同时标记是否为本地文献"""
        if self.source_type == 'wos':
            check_cols = ['PY','J9','VL','BP']
        elif self.source_type in ['cssci','scopus']:
            check_cols = ['first_AU','TI']
        else:
            raise ValueError('Invalid source type')
        use_cols = self.reference_table.columns.tolist()[:-1]  
        reference_table = self.reference_table.groupby(use_cols,as_index=False).size()
        reference_table = reference_table.sort_values(by='size',ascending=False)
        reference_table = reference_table.rename(columns={'size':'Recs'})
        common_table = reference_table.reset_index().merge(self.docs_table[check_cols],on=check_cols)
        reference_table['local'] = 0
        reference_table.loc[common_table['index'],'local'] = 1
        return reference_table
    
    def write2excel(self,save_path:str):
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
            
            if self.source_type in ['wos','cssci']:
                self._generate_institution_table().to_excel(writer,sheet_name='Institutions')
            if self.source_type in ['wos','scopus']:
                self._generate_document_type_table().to_excel(writer,sheet_name='Document Type')