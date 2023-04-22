import pandas as pd

class GraphViz:

    def __init__(self,citation_table):
        self.citation_table = citation_table
        self.year_empty_index = set(citation_table[citation_table['PY'].isna()].index)

    def __obtain_groups(self):
        """obtain groups of docs by year"""

        year_series = self.citation_table.loc[self.node_list,'PY']
        groups = year_series.groupby(year_series)
        year_list = [i[0] for i in groups]
        grouped_doc_index = [i[1].index.tolist() for i in groups]
        self.year_list = year_list
        for idx,year in enumerate(year_list):
            grouped_doc_index[idx].insert(0,year)
        self.grouped_doc_index = grouped_doc_index
    
    def __generate_edge(self,doc_index:int,doc_relation:str,relation_type:str):

        # filter docs with empty year
        related_doc_list = [int(i) for i in doc_relation.split(';') if int(i) not in self.year_empty_index]
        if relation_type=='reference':
            return {(doc_index,ref) for ref in related_doc_list}
        elif relation_type=='citation':
            return {(citation,doc_index) for citation in related_doc_list}
        
    def __generate_edge_list(self):
        min_df = self.citation_table.loc[self.doc_indices,['reference','citation']]
        edge_set = set()
        for idx in self.doc_indices:
            doc_index = idx
            doc_reference = min_df.loc[idx,'reference']
            doc_citation = min_df.loc[idx,'citation']
            if pd.notna(doc_citation):
                edge_set.update(self.__generate_edge(doc_index, doc_citation, 'citation')) # type:ignore
            if pd.notna(doc_reference):
                edge_set.update(self.__generate_edge(doc_index, doc_reference,'reference')) # type: ignore
        
        # 过滤索引列表之外的文献
        if not self.allow_external_node:
            edge_set = [(edge[0],edge[1]) for edge in edge_set if edge[0] in self.doc_indices and edge[1] in self.doc_indices]
        
        # 根据边生成节点
        source_node = set([i for i,_ in edge_set])
        target_node = set([j for _,j in edge_set])
        node_list = sorted(source_node|target_node)
        self.node_list = node_list

        edge_list = {i:[] for i in sorted(source_node)}
        for edge in edge_set:
            edge_list[edge[0]].append(edge[1])

        return edge_list
        
    def generate_dot_file(self,doc_indices,allow_external_node=False):
        """生成dot文件
        doc_indices: 文献索引列表;
        allow_external_node: 是否允许出现doc_indices之外的节点，默认False
        """
        self.doc_indices = [i for i in doc_indices if i not in self.year_empty_index]
        self.allow_external_node = allow_external_node

        raw_edge_list = self.__generate_edge_list()
        self.__obtain_groups()
        
        # dot_edge_list = [f'\t{edge[0]} -> {edge[1]};\n' for edge in raw_edge_list]
        dot_edge_list = [f'\t{source} -> '+'{ '+' '.join([str(i) for i in raw_edge_list[source]])+' };\n' for source in raw_edge_list]
        dot_groups = [f'\t{{rank=same; {" ".join([str(i) for i in group_index])}}};\n' for group_index in self.grouped_doc_index]
        
        reverse_year_list = self.year_list[::-1]
        year_edge_list = [(year,reverse_year_list[idx+1]) for idx,year in enumerate(reverse_year_list) if idx < len(reverse_year_list)-1]
        dot_year_node_list = [f'\t{year} [ shape="plaintext" ];\n' for year in self.year_list]
        dot_year_edge_list = [f'\t{edge[0]} -> {edge[1]} [ style = invis ];\n' for edge in year_edge_list]
        dot_text = 'digraph metadata{\n\trankdir = BT;\n'

        for dot_group in dot_groups:
            dot_text += dot_group

        for dot_year_node in dot_year_node_list:
            dot_text += dot_year_node
        
        for dot_year_edge in dot_year_edge_list:
            dot_text += dot_year_edge
            
        for dot_edge in dot_edge_list:
            dot_text += dot_edge
        dot_text += '}'
        return dot_text
    
    @staticmethod
    def __extract_first_author(au_cell:str):
        """提取一作"""
        return au_cell.split(';',1)[0].replace(',','')
    
    def generate_graph_node_file(self)->pd.DataFrame:
        use_cols = ['doc_index','AU','PY','SO','VL','BP','LCS','TC']
        graph_node_table = self.citation_table.loc[self.node_list,use_cols]
        graph_node_table['AU'] = graph_node_table['AU'].apply(self.__extract_first_author)
        graph_node_table = graph_node_table.rename(columns={'TC':'GCS'})
        return graph_node_table