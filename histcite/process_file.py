import os
import re
import pandas as pd
from histcite.parse_reference import ParseReference
from histcite.recognize_reference import RecognizeReference

class ProcessWosFile:
    @staticmethod
    def extract_first_author(au_cell:str):
        return au_cell.split(';',1)[0].replace(',','')

class ProcessCssciFile:
    @staticmethod
    def process_org(cell):
        org_set = set(re.findall(r'](.*?)(?:/|$)',cell))
        org_list = [i.replace('.','') for i in org_set]
        return '; '.join(org_list)

class ProcessScopusFile:
    @staticmethod
    def extract_first_author(au_field:pd.Series):
        return au_field.str.split(pat=';',n=1,expand=True)[0]
    
class ReadFile:
    @staticmethod
    def _read_csv(file_path:str,use_cols:list,sep:str=',')->pd.DataFrame:
        try:
            df = pd.read_csv(
                file_path,
                sep=sep,
                header=0,
                on_bad_lines='skip',
                usecols=use_cols,
                dtype_backend="pyarrow")
            return df
        except ValueError:
            file_name = os.path.basename(file_path)
            raise ValueError(f'File {file_name} is not a valid csv file')
        
class ProcessFile:

    def __init__(self,folder_path:str,source_type:str):
        """
        folder_path: 文件夹路径\n
        source_type: 数据来源 wos|cssci|scopus|pubmed
        """
        self.folder_path = folder_path
        self.source_type = source_type
        if source_type=='wos':
            self.file_name_list = [i.split('.')[0] for i in os.listdir(folder_path) if i[:9]=='savedrecs']
        elif source_type=='cssci':
            self.file_name_list = [i for i in os.listdir(folder_path) if i[:3]=='LY_']
        elif source_type=='scopus':
            self.file_name_list = [i.split('.')[0] for i in os.listdir(folder_path) if i[:6]=='scopus']
        else:
            raise ValueError('Invalid source type')
        
        self.file_name_list.sort()
        if source_type == 'wos':
            self.file_name_list = [i+'.txt' for i in self.file_name_list]
        elif source_type == 'scopus':
            self.file_name_list = [i+'.csv' for i in self.file_name_list]

    def _read_wos_file(self,file_name:str)->pd.DataFrame:
        """读取wos表单"""
        use_cols = ['AU','TI','SO','DT','CR','DE','C3','NR','TC','Z9','J9','PY','VL','BP','DI','UT']
        file_path = os.path.join(self.folder_path,file_name)
        df = ReadFile._read_csv(file_path,use_cols,'\t')
        
        # 转换数据类型
        df['BP'] = df['BP'].apply(pd.to_numeric,errors='coerce')
        df['VL'] = df['VL'].apply(pd.to_numeric,errors='coerce')
        df = df.astype({'BP':'int64[pyarrow]', 'VL':'int64[pyarrow]'})
        
        # 提取一作
        first_au = df['AU'].apply(ProcessWosFile.extract_first_author)
        df.insert(1,'first_AU',first_au)
        df['source file'] = file_name
        return df
    
    def _read_cssci_file(self,file_name:str)->pd.DataFrame:
        """读取cssci文本文件"""
        file_path = os.path.join(self.folder_path,file_name)
        with open(file_path,'r') as f:
            text = f.read()
        
        if text[:16] != '南京大学中国社会科学研究评价中心':
            raise ValueError(f'File {file_name} is not a valid cssci file')
        body_text = text.split('\n\n\n',1)[1]
        contents = {}
        original_fields = ['来源篇名','来源作者','基    金','期    刊','第一机构','机构名称','第一作者','年代卷期','关 键 词','参考文献']
        for field in original_fields:
            if field != '参考文献':
                field_pattern = f'【{field}】(.*?)\n'
                contents[field] = re.findall(field_pattern,body_text)
            else:
                field_pattern = '【参考文献】\n(.*?)\n?'+'-'*5
                contents[field] = re.findall(field_pattern,body_text,flags=re.S)
        
        df = pd.DataFrame.from_dict(contents)
        df.columns = ['TI','AU','FU','SO','first_org','C3','first_AU','PY&VL&BP&EP','DE','CR']
        df['AU'] = df['AU'].str.replace('/','; ')
        df['DE'] = df['DE'].str.replace('/','; ')
        df['PY'] = df['PY&VL&BP&EP'].str.extract(r'^(\d{4}),',expand=False)
        df['C3'] = df['C3'].apply(ProcessCssciFile.process_org)
        df['CR'] = df['CR'].str.replace('\n','; ')
        df['NR'] = df['CR'].str.count('; ')
        df['source file'] = file_name
        return df
    
    def _read_scopus_file(self,file_name:str)->pd.DataFrame:
        """读取scopus表单"""
        use_cols = ['Authors','Author full names','Title','Year','Source title','Volume','Issue','Cited by','DOI','Affiliations','Author Keywords','References','Document Type','EID']
        file_path = os.path.join(self.folder_path,file_name)
        df = ReadFile._read_csv(file_path,use_cols)
        df.columns = ['AU','Author full names','TI','PY','SO','VL','IS','TC','DI','C3','DE','CR','DT','EID']
        df['NR'] = df['CR'].str.count('; ')
        df['first_AU'] = ProcessScopusFile.extract_first_author(df['AU'])
        df['source file'] = file_name
        return df
    
    def concat_table(self):
        """合并多个dataframe"""
        if len(self.file_name_list)>1:
            if self.source_type=='wos':
                docs_table = pd.concat([self._read_wos_file(file_name) for file_name in self.file_name_list],ignore_index=True,copy=False)
            elif self.source_type=='cssci':
                docs_table = pd.concat([self._read_cssci_file(file_name) for file_name in self.file_name_list],ignore_index=True,copy=False)
            elif self.source_type=='scopus':
                docs_table = pd.concat([self._read_scopus_file(file_name) for file_name in self.file_name_list],ignore_index=True,copy=False)
            else:
                raise ValueError('Invalid source type')
        
        elif len(self.file_name_list)==1:
            if self.source_type=='wos':
                docs_table = self._read_wos_file(self.file_name_list[0])
            elif self.source_type=='cssci':
                docs_table = self._read_cssci_file(self.file_name_list[0])
            elif self.source_type=='scopus':
                docs_table = self._read_scopus_file(self.file_name_list[0])
            else:
                raise ValueError('Invalid source type')
        
        else:
            raise FileNotFoundError('No valid file in the folder')
        
        original_num = docs_table.shape[0]
        # 删除重复数据
        if self.source_type=='wos':
            docs_table.drop_duplicates(subset=['UT'],ignore_index=True,inplace=True) # 根据入藏号删除重复数据
        elif self.source_type=='cssci':
            docs_table.drop_duplicates(subset=['TI','first_AU'],ignore_index=True,inplace=True) # 根据题名和一作删除重复数据
        elif self.source_type=='scopus':
            docs_table.drop_duplicates(subset=['EID'],ignore_index=True,inplace=True) # 根据eid删除重复数据
        current_num = docs_table.shape[0]
        print(f'共读取 {original_num} 条数据，去重后剩余 {current_num} 条')
        
        # 按照年份进行排序
        # docs_table = docs_table.sort_values(by='PY',ignore_index=True)
        docs_table.insert(0,'doc_index',docs_table.index)

        # scopus题名转小写
        if self.source_type == 'scopus':
            self.TI_COPY = docs_table['TI'].copy()
            docs_table['TI'] = docs_table['TI'].str.lower()
        
        self.docs_table = docs_table
        return docs_table
    
    def __generate_reference_table(self,cr_series:pd.Series):
        """生成参考文献表格"""
        if self.source_type=='wos':
            parsed_cr_cells = [ParseReference(doc_index,cell,'wos').parse_cr_cell() for doc_index,cell in cr_series.items()]
            reference_table = pd.concat([pd.DataFrame.from_dict(cell) for cell in parsed_cr_cells if cell],ignore_index=True)
            reference_table = reference_table.astype({'PY':'int64[pyarrow]', 'VL':'int64[pyarrow]', 'BP':'int64[pyarrow]'})
        
        elif self.source_type=='cssci':
            parsed_cr_cells = [ParseReference(doc_index,cell,'cssci').parse_cr_cell() for doc_index,cell in cr_series.items()]
            reference_table = pd.concat([pd.DataFrame.from_dict(cell) for cell in parsed_cr_cells if cell],ignore_index=True)
         
        elif self.source_type=='scopus':
            parsed_cr_cells = [ParseReference(doc_index,cell,'scopus').parse_cr_cell() for doc_index,cell in cr_series.items()]
            reference_table = pd.concat([pd.DataFrame.from_dict(cell) for cell in parsed_cr_cells if cell],ignore_index=True)

        else:
            raise ValueError('Invalid source type')
        self.reference_table = reference_table
    
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
        
        if self.source_type=='wos':
            reference_field = self.docs_table.apply(lambda row:RecognizeReference.recognize_wos_reference(self.docs_table,self.reference_table,row.name),axis=1)
        elif self.source_type=='cssci':
            reference_field = self.docs_table.apply(lambda row:RecognizeReference.recognize_cssci_reference(self.docs_table,self.reference_table,row.name),axis=1)
        elif self.source_type=='scopus':
            reference_field = self.docs_table.apply(lambda row:RecognizeReference.recognize_scopus_reference(self.docs_table,self.reference_table,row.name),axis=1)
        else:
            raise ValueError('Invalid source type')
        
        citation_field = self.__reference2citation(reference_field)
        lcr_field = reference_field.apply(len)
        lcs_field = citation_field.apply(len)
        self.docs_table['reference'] = [';'.join([str(j) for j in i]) if i else None for i in reference_field]
        self.docs_table['citation'] = [';'.join([str(j) for j in i]) if i else None for i in citation_field]
        self.docs_table['LCR'] = lcr_field
        self.docs_table['LCS'] = lcs_field

        if self.source_type == 'scopus':
            self.docs_table['TI'] = self.TI_COPY