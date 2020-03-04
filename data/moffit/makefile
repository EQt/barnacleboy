# see Dryad API: http://wiki.datadryad.org/Data_Access#DataONE_API
DOI = doi:10.5061/dryad.8t8s248
URL = https://datadryad.org/resource/${DOI}
PYDIR = ../../python


all: raw/pixel.csv raw/pixel.meta.xml raw/paper.xml example.csv.gz example.graph.h5


raw/pixel.zip:
	mkdir -p raw
	wget -O $@ https://datadryad.org/stash/downloads/download_resource/20150

raw/pixel.csv: raw/pixel.zip
	unzip -p $< > $@
	md5sum -c pixel.md5
	touch $@

raw/paper.xml:
	curl ${URL}?XML > $@


raw/pixel.meta.xml:
	curl ${URL}/1?XML > $@


example.csv.gz: raw/pixel.csv prior.py
	python prior.py -o $@


%.graph.h5: %.csv.gz ${PYDIR}/graph.py
	python ${PYDIR}/graph.py -o $@ $<
