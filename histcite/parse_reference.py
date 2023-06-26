import re

class ParseScopusCR:
	@staticmethod
	def parse_author(cr:str,TI:str):
		left_cr = cr.replace(TI,'')
		try:
			first_AU = left_cr.split(',',1)[0]
			if re.match('[A-Za-z]',first_AU):
				return first_AU
			else:
				return None
		except TypeError:
			return None
	
	@staticmethod
	def check_title(TI:str):
		if re.match(r'^[A-Z\d\'\"‘“]',TI):
			return TI.strip(',.;?').lower()
		
class ParseReference:
	def __init__(self,doc_index,cr_cell:str,source_type:str):
		"""Parse citation records from a cr cell
		doc_index: index of the record
		cr_cell: cr cell
		source_type: wos|cssci|scopus
		"""
		sep = '; '
		try:
			self.cr_list = cr_cell.split(sep)
			self.cr_count = len(self.cr_list)
		except AttributeError:
			self.cr_count = 0
		else:
			self.doc_index = doc_index
			self.source_type = source_type

	@staticmethod
	def _parse_wos_cr(cr:str):
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
	def _parse_cssci_cr(cr:str):
		au_pattern = re.compile(r'(?<!\d)\.(?!\d)|(?<=\d)\.(?!\d)|(?<!\d)\.(?=\d)|(?<=\d{4})\.(?=\d{4})')
		# 中文参考文献
		if re.search(r'[\u4e00-\u9fa5]',cr):
			try:
				_,AU,TI,_ = au_pattern.split(cr,3)
				if ',' not in AU:
					return {'first_AU':AU,'TI':TI}
			except ValueError:
				return None
	
		# 英文参考文献
		else:
			if index_AU := re.search(r'^(\d+\.(.*?))\.[A-Za-z"“\d]{1}[a-zA-Z\s\d]+',cr):
				AU = index_AU.group(2)
				if AU !='':
					other = cr.replace(index_AU.group(1),'')
					try:
						_,TI,_ = au_pattern.split(other,2)
						return {'first_AU':AU,'TI':TI}
					except ValueError:
						return None
				else:
					try:
						_,_,TI,_ = au_pattern.split(cr,3)
					except ValueError:
						_,_,TI,_ = cr.split('.',3)
					return {'first_AU':AU,'TI':TI}

	@staticmethod
	def _parse_scopus_cr(cr:str):
		# 从中间开始匹配，长文本，不包含逗号
		pattern1 = r'\.?,\s(([^\.\s,]+\s){3,}[^\.\s,]+(,|\?|\.|;|\s))'
		# 从中间开始匹配，长文本，包含逗号
		pattern2 = r'\.?,\s(([^\.\s]+\s){3,}[^\.\sA-Z]+(,|\?|\.|;))\s[A-Z(]'
		# 从头开始匹配，长文本，不包含逗号
		pattern3 = r'^(([^\.\s,]+\s){3,}[^\.\s,]+(,|\?|\.|;))'
		# 从中间开始匹配，短文本，不包括逗号
		pattern4 = r'\.?,\s([^\.,\d]+)(?=,)'

		try:
			TI = re.search(pattern1,cr)[1] # type: ignore
		except TypeError:
			try:
				TI = re.search(pattern3,cr)[1] # type: ignore
			except TypeError:
				try:
					TI = re.search(pattern4,cr)[1] # type: ignore
				except TypeError:
					return None
		else:
			if re.match('^[a-z]',TI):
				try:
					TI = re.search(pattern2,cr)[1] # type: ignore
				except TypeError:
					return None
		
		scopus_parser = ParseScopusCR()
		TI = scopus_parser.check_title(TI)
		if TI:
			first_AU = scopus_parser.parse_author(cr,TI)
			return {'first_AU':first_AU,'TI':TI}

	def parse_cr_cell(self):
		if self.cr_count == 0:
			return None
		
		if self.source_type == "wos":
			parsed_cr_list = [self._parse_wos_cr(i) for i in self.cr_list]
			keys = ['first_AU','PY','J9','VL','BP','DI']
		elif self.source_type == "cssci":
			parsed_cr_list = [self._parse_cssci_cr(i) for i in self.cr_list]
			keys = ['first_AU','TI']
		elif self.source_type == "scopus":
			parsed_cr_list = [self._parse_scopus_cr(i) for i in self.cr_list]
			keys = ['first_AU','TI']
		else:
			raise ValueError('Invalid source type')
		
		result = {key:[] for key in keys}
		for single in parsed_cr_list:
			if single is not None:
				for key in keys:
					result[key].append(single[key])
		result['doc_index'] = self.doc_index
		return result