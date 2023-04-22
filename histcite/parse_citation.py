import re
import pandas as pd

class ParseCitation:
    
    def __init__(self,doc_index,cr_cell:str):
        self.error = False
        try:
            self.cr_list = cr_cell.split('; ')
        except AttributeError:
            self.error = True
        self.doc_index = doc_index
        self.keys = ['AU','PY','J9','VL','BP','DI']

    def __parse_one_cr(self,cr):
        """Parse a single citation record"""
        AU,PY,J9,VL,BP,DI = None,None,None,None,None,None
        cr_data = {}

        try:
            AU,PY,J9,other = re.split(r', (?![^\[\]]*\])',cr,3)
        except ValueError:
            if len(_ := re.split(r', (?![^\[\]]*\])',cr,2))==3:
                AU,PY,J9 = _

        else:
            if VL:= re.search(r'V(\d+)',other):
                VL = VL.group(1)
                try:
                    VL = int(VL)
                except ValueError:
                    VL = None

            if BP:= re.search(r'P(\d+)',other):
                BP = BP.group(1)
                try:
                    BP = int(BP)
                except ValueError:
                    BP = None

            if DI:= re.search(r'DOI (10.*)$',other):
                DI = DI.group(1)
                if '[' in DI or ']' in DI:
                    DI = None
                                            
        finally:
            # AU strip
            if isinstance(AU,str):
                cr_data['AU'] = AU.strip()
            else:
                return None
        
            # check year
            if PY:
                if re.match(r'^\d{4}$',PY):
                    PY = int(PY)
                    cr_data['PY'] = PY
                else:
                    return None
                
            cr_data['J9'] = J9
            cr_data['VL'] = VL 
            cr_data['BP'] = BP 
            cr_data['DI'] = DI 
            return cr_data
    
    def parse_cr_cell(self):
        if self.error:
            return None
        result = {key:[] for key in self.keys}
        parsed_cr_list = [self.__parse_one_cr(i) for i in self.cr_list]
        for single in parsed_cr_list:
            if single is not None:
                for key in self.keys:
                    result[key].append(single[key])
        
        result['doc_index'] = self.doc_index
        return result
    
    def export_citation_table(self):
        parsed_result = self.parse_cr_cell()
        if parsed_result:
            return pd.DataFrame.from_dict(parsed_result)