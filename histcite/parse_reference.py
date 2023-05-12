import re

class ParseReference:
    def __init__(self,doc_index,cr_cell:str,source_type:str):
        """Parse citation records from a cr cell
        doc_index: index of the record
        cr_cell: cr cell
        source_type: wos|cssci
        """
        if source_type=='wos':
            sep = '; '
        elif source_type=='cssci':
            sep = '\n'
        else:
            raise ValueError('Invalid source type')
        
        try:
            self.cr_list = cr_cell.split(sep)
            self.cr_count = len(self.cr_list)
        except AttributeError:
            self.cr_count = 0
        self.doc_index = doc_index
        self.source_type = source_type

    @staticmethod
    def __parse_wos_cr(cr):
        """Parse a single citation record"""
        AU,PY,J9,VL,BP,DI = None,None,None,None,None,None
        cr_data = {}

        try:
            AU,PY,J9,other = re.split(r', (?![^\[\]]*\])',cr,3)
        except ValueError:
            if len(fields := re.split(r', (?![^\[\]]*\])',cr,2))==3:
                AU,PY,J9 = fields
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
            if isinstance(AU,str):
                cr_data['first_AU'] = AU.strip(', ')
            else:
                return None
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
    
    @staticmethod
    def __parse_cssci_cr(cr):

        # 中文参考文献
        if re.search(r'[\u4e00-\u9fa5]',cr):
            try:
                _,AU,TI,_ = cr.split('.',3)
                if ',' not in AU:
                    return {'first_AU':AU,'TI':TI}
            except ValueError:
                return None
    
        # 英文参考文献
        else:
            if AU := re.search(r'^\d+\.(.*?)\.[A-Z]+[a-z]+',cr):
                AU = AU.group(1)
                if AU !='':
                    other = cr.replace(f'{AU}.','')
                    try:
                        _,TI,_ = other.split('.',2)
                        return {'first_AU':AU,'TI':TI}
                    except ValueError:
                        return None
                        
                else:
                    _,_,TI,_ = cr.split('.',3)
                    return {'first_AU':AU,'TI':TI}
            
    def parse_cr_cell(self):
        if self.cr_count == 0:
            return None
        
        if self.source_type == "wos":
            parsed_cr_list = [self.__parse_wos_cr(i) for i in self.cr_list]
            keys = ['first_AU','PY','J9','VL','BP','DI']
        elif self.source_type == "cssci":
            parsed_cr_list = [self.__parse_cssci_cr(i) for i in self.cr_list]
            keys = ['first_AU','TI']
        else:
            raise ValueError()
        
        result = {key:[] for key in keys}
        for single in parsed_cr_list:
            if single is not None:
                for key in keys:
                    result[key].append(single[key])
        
        result['doc_index'] = self.doc_index
        return result