# see Dryad API: http://wiki.datadryad.org/Data_Access#DataONE_API
DOI = doi:10.5061/dryad.8t8s248
URL = https://datadryad.org/resource/${DOI}


all: raw/pixel.csv raw/pixel.meta.xml raw/paper.xml


raw/pixel.csv:
	wget -O $@ https://datadryad.org/mn/object/${DOI}/1/bitstream
	md5sum -c pixel.md5
	touch $@


raw/paper.xml:
	curl ${URL}?XML > $@


raw/pixel.meta.xml:
	curl ${URL}/1?XML > $@
