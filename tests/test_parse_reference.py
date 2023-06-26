from histcite.parse_reference import ParseReference

def test_wos_cr():
    cr_cell = 'Bengio Y, 2001, ADV NEUR IN, V13, P932; Chang Y, 2003, IEEE INTERNATIONAL WORKSHOP ON ANALYSIS AND MODELING OF FACE AND GESTURES, P28; Chen Z., 2000, 6 INT C SPOK LANG PR; CORTES C, 1995, MACH LEARN, V20, P273, DOI 10.1007/BF00994018; '
    parsed_citation_dict = ParseReference(0,cr_cell,'wos').parse_cr_cell()
    assert parsed_citation_dict is not None
    assert parsed_citation_dict['first_AU'][0]=='Bengio Y'
    assert parsed_citation_dict['PY'][0]==2001
    assert parsed_citation_dict['J9'][0]=='ADV NEUR IN'
    assert parsed_citation_dict['VL'][0]==13
    assert parsed_citation_dict['BP'][0]==932

def test_cssci_cr():
    cr_cell = '1..2021年度江苏省公共图书馆大数据统计报告; 2.吴建中.建设智慧图书馆，我们准备好了吗？.2022;'
    parsed_citation_dict = ParseReference(0,cr_cell,'cssci').parse_cr_cell()
    assert parsed_citation_dict is not None
    assert parsed_citation_dict['first_AU'][0]=='吴建中'
    assert parsed_citation_dict['TI'][0]=='建设智慧图书馆，我们准备好了吗？'

def test_scopus_cr():
    cr_cell = 'Aone C., Halverson L., Hampton T., Ramos-Santacruz M., Sra: Description of the ie2 system used for muc-7, In Seventh Message Understanding Conference (MUC-7): Proceedings of a Conference Held in Fairfax, 1998, (1998); Appelt D., Et al., Sri International Fastus Systemmuc-6 Test Results and Analysis. in Sixth Message Understanding Conference (MUC-6): Proceedings of a Conference Held in Columbia, (1995); '
    parsed_citation_dict = ParseReference(0,cr_cell,'scopus').parse_cr_cell()
    assert parsed_citation_dict is not None
    assert parsed_citation_dict['first_AU'][0]=='Aone C.'
    assert parsed_citation_dict['first_AU'][1]=='Appelt D.'
    assert parsed_citation_dict['TI'][0]=='sra: description of the ie2 system used for muc-7'
