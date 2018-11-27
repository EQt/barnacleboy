"""
Download the files to the paper
"Molecular, spatial, and functional single-cell profiling of the hypothalamic preoptic region"
by Jeffrey R. Moffitt et al. 2018
http://science.sciencemag.org/content/362/6416/eaau5324
"""
from os import path
import GEOparse


if __name__ == '__main__':

    debug = False
    download_sra = False
    gse_id = "GSE113576"
    raw_dir = path.join(path.dirname(__file__), './raw')
    

    if debug:
        GEOparse.set_verbosity("DEBUG")
    gse = GEOparse.get_GEO(geo=gse_id, destdir=raw_dir)
    for n, meta in gse.metadata.items():
        if 'supplementary_file' in n:
            for url in meta:
                dest = path.join(raw_dir, url.split('/')[-1])
                if not path.exists(dest):
                    GEOparse.utils.download_from_url(url, dest, force=False)


    for gsm, samp1 in gse.gsms.items():
        break

    if download_sra:
        samp1.download_SRA('bla@bla.com', directory=raw_dir)
