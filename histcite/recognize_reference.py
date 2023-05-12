import pandas as pd

class RecognizeReference:
    """识别参考文献"""

    def __init__(self,docs_table:pd.DataFrame, reference_table:pd.DataFrame) -> None:
        self.docs_table = docs_table
        self.reference_table = reference_table

    def recognize_wos_reference(self,row_index,merge_method=False)->list:
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
        
        if merge_method:
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
    
    def recognize_cssci_reference(self,row_index,merge_method=False)->list:
        local_ref_list = []
        compare_cols = ['first_AU','TI']
        child_reference_table = self.reference_table[self.reference_table['doc_index']==row_index].dropna(subset=compare_cols)
        row_year = self.docs_table.loc[row_index,'PY']
        child_docs_table = self.docs_table[self.docs_table['PY']<=row_year].dropna(subset=compare_cols)

        if merge_method:
            common_table = child_docs_table[['doc_index']+compare_cols].merge(child_reference_table[compare_cols])
            if common_table.shape[0]>0:
                common_table = common_table.drop_duplicates(subset='doc_index',ignore_index=True)
                local_ref_list.extend(common_table['doc_index'].tolist())
        else:
            for idx,row_data in child_docs_table.iterrows():
                for _,child_reference in child_reference_table.iterrows():
                    if all(row_data[col]==child_reference[col] for col in compare_cols):
                        local_ref_list.append(idx)
        return local_ref_list