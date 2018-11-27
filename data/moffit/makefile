# see Dryad API: http://wiki.datadryad.org/Data_Access#DataONE_API
DOI = doi:10.5061/dryad.8t8s248
URL = https://datadryad.org/resource/${DOI}


all: raw/pixel.csv raw/pixel.meta.xml raw/paper.xml


raw/pixel.csv:
	wget -O $@ ${URL}/1/bitstream
	touch $@


raw/paper.xml:
	curl ${URL}?XML > $@


raw/pixel.meta.xml:
	curl ${URL}/1?XML > $@
