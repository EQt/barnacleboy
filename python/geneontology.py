"""
Query GeneOntology from BioSmart service
"""
from os import path
import pandas as pd
import biomart


cb_path = "../data/codebook.csv"
out_path = "../data/ontology.tsv"
codes = pd.read_csv(cb_path, skiprows=3, skipinitialspace=True)
gene_ids = codes['id'].dropna().tolist()


server = biomart.BiomartServer('http://www.ensembl.org/biomart')
data = server.datasets['hsapiens_gene_ensembl']

res = data.search({
    'filters': {'ensembl_transcript_id_version': gene_ids},
    'attributes': [
        'ensembl_transcript_id_version',
        'ensembl_gene_id',
        'name_1006',
        'go_id',
        'namespace_1003'
    ]})
assert res.ok

with open(out_path, 'w') as io:
    io.write(res.text)
