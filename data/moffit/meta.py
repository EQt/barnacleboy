"""
Extract description of the CSV columns of 
"""
from lxml import etree
from io import BytesIO


fname = 'raw/pixel.meta.xml'
xml = etree.parse(fname)
ns = xml.getroot().nsmap[None]

head, = xml.xpath('//i:metadata[@element="xhtml_head_item"]', namespaces={'i': ns})

content = etree.tostring(head)
content = content.replace(b"&gt;", b">")
content = content.replace(b"&lt;", b"<")

io = BytesIO(content)
x = etree.parse(io)
assert ns == x.getroot().nsmap[None]    # same namespace

[descr] = x.xpath('//i:meta[@name="DC.description"]/@content', namespaces={'i': ns})

items = descr.split('. “')
print(items[0] + ':')
print()
print("\n\n".join("“" + s for s in items[1:]))
