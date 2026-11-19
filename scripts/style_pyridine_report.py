from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
from copy import deepcopy
import re
ROOT = Path(__file__).resolve().parents[1]
base = ROOT / 'frontend/public/reports'
ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
w = '{'+ns['w']+'}'
source = base/'pyridine/engineering-report-r05.docx'
target = base/'pyridine/engineering-report-r06.docx'
with ZipFile(base/'pdh/engineering-report-r05.docx') as z:
    reference = E.fromstring(z.read('word/document.xml'))
borders = reference.find('.//w:tblPr/w:tblBorders',ns)
def prop(parent, name, **attrs):
    el=parent.find(w+name)
    if el is None:
        el=E.SubElement(parent,w+name)
    for key,value in attrs.items(): el.set(w+key,str(value))
    return el
with ZipFile(source) as zin:
    root=E.fromstring(zin.read('word/document.xml'))
    for table in root.findall('.//w:body/w:tbl',ns):
        properties=table.find(w+'tblPr')
        old=properties.find(w+'tblBorders')
        if old is not None: properties.remove(old)
        properties.append(deepcopy(borders))
        for ri,row in enumerate(table.findall(w+'tr')):
            rowpr=prop(row,'trPr')
            prop(rowpr,'cantSplit')
            if ri==0: prop(rowpr,'tblHeader')
            for cell in row.findall(w+'tc'):
                cp=cell.find(w+'tcPr')
                prop(cp,'shd',fill='DFEAF2' if ri==0 else 'FFFFFF',val='clear')
                prop(cp,'vAlign',val='center')
                for paragraph in cell.findall(w+'p'):
                    pp=paragraph.find(w+'pPr')
                    if pp is None:
                        pp=E.Element(w+'pPr'); paragraph.insert(0,pp)
                    prop(pp,'spacing',before='40',after='40',line='240',lineRule='auto')
                    text=''.join(paragraph.itertext())
                    text=''.join(paragraph.xpath('.//w:t/text()',namespaces=ns))
                    is_numeric=bool(re.match(r'^[≥≤<>+−\-]?\d[\d,.]*(?:\s|%|$)',text))
                    prop(pp,'jc',val='right' if ri>0 and is_numeric else 'left')
                    for run in paragraph.findall(w+'r'):
                        rp=run.find(w+'rPr')
                        if rp is None:
                            rp=E.Element(w+'rPr');run.insert(0,rp)
                        prop(rp,'rFonts',eastAsia='SimHei')
                        prop(rp,'sz',val='18');prop(rp,'szCs',val='18')
    with ZipFile(target,'w',ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True) if item.filename=='word/document.xml' else zin.read(item.filename)
            zout.writestr(item,data)
print(target)