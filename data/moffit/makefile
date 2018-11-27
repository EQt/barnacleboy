all: raw/pixel.csv raw/pixel.meta.xml

raw/pixel.csv:
	wget -O $@ https://datadryad.org/bitstream/handle/10255/dryad.192695/Moffitt_and_Bambah-Mukku_et_al_merfish_all_cells.csv?sequence=1
	touch $@

raw/pixel.meta.xml:
	curl "https://datadryad.org/resource/doi:10.5061/dryad.8t8s248/DIR" > $@
