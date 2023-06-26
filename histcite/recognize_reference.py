import pandas as pd

class RecognizeCommonReference:
    def __init__(self,docs_table:pd.DataFrame, reference_table:pd.DataFrame):
        self.docs_table = docs_table
        self.reference_table = reference_table

    def filter_tables(self,row_index,compare_cols:list)->tuple:
        assert set(compare_cols+['PY','doc_index']).issubset(self.docs_table.columns)
        assert set(compare_cols).issubset(self.reference_table.columns)

        row_year = self.docs_table.loc[row_index,'PY']
        child_reference_table = self.reference_table[self.reference_table['doc_index']==row_index].dropna(subset=compare_cols)
        child_docs_table = self.docs_table[self.docs_table['PY']<=row_year].dropna(subset=compare_cols)
        return child_docs_table,child_reference_table
    
    def recognize_ref(self,child_docs_table:pd.DataFrame,
                            child_reference_table:pd.DataFrame,
                            compare_cols:list,
                            merge_method:bool)->list:
        
        local_ref_list = []
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


class RecognizeReference():
    """识别参考文献"""
    @staticmethod
    def recognize_wos_reference(docs_table:pd.DataFrame,
                                reference_table:pd.DataFrame,
                                row_index:int)->list:
        
        local_ref_list = []
        child_reference_table = reference_table[reference_table['doc_index']==row_index]
        
        # 存在DOI
        child_reference_table_doi = child_reference_table[child_reference_table['DI'].notna()]['DI']
        child_docs_table_doi = docs_table[docs_table['DI'].notna()]['DI']
        local_ref_list.extend(child_docs_table_doi[child_docs_table_doi.isin(child_reference_table_doi)].index.tolist())
        
        # 不存在DOI
        compare_cols = ['first_AU','PY','J9','BP']
        child_reference_table_left = child_reference_table[child_reference_table['DI'].isna()].dropna(subset=compare_cols)
        child_reference_py = child_reference_table_left['PY']
        child_reference_bp = child_reference_table_left['BP']

        # 年份符合，页码符合，doi为空
        recognize_instance = RecognizeCommonReference(docs_table,reference_table)
        child_docs_table_left = docs_table[(docs_table['PY'].isin(child_reference_py))&(docs_table['BP'].isin(child_reference_bp)&docs_table['DI'].isna())].dropna(subset=compare_cols)
        local_ref_list.extend(recognize_instance.recognize_ref(child_docs_table_left,child_reference_table_left,compare_cols,merge_method=True))
        
        try:
            local_ref_list.remove(row_index)
        except ValueError:
            pass
        return local_ref_list
    
    @staticmethod
    def recognize_cssci_reference(docs_table:pd.DataFrame,
                                  reference_table:pd.DataFrame,
                                  row_index:int)->list:
        
        compare_cols = ['first_AU','TI']
        recognize_instance = RecognizeCommonReference(docs_table,reference_table)
        child_docs_table,child_reference_table = recognize_instance.filter_tables(row_index,compare_cols)
        result = recognize_instance.recognize_ref(child_docs_table,child_reference_table,compare_cols,merge_method=True)
        try:
            result.remove(row_index)
        except ValueError:
            pass
        return result
    
    @staticmethod
    def recognize_scopus_reference(docs_table:pd.DataFrame,
                                   reference_table:pd.DataFrame,
                                   row_index:int)->list:
        compare_cols = ['first_AU','TI']
        recognize_instance = RecognizeCommonReference(docs_table,reference_table)
        child_docs_table,child_reference_table = recognize_instance.filter_tables(row_index,compare_cols)
        result = recognize_instance.recognize_ref(child_docs_table,child_reference_table,compare_cols,merge_method=True)
        try:
            result.remove(row_index)
        except ValueError:
            pass
        return result