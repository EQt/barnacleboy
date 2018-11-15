"""
Query GeneOntology from BioSmart service
"""
import pandas as pd
import sys
from os import path


cb_path = "../data/codebook.csv"
out_path = "../data/ontology.tsv"
columns = [
    'ensembl_transcript_id_version',
    'ensembl_gene_id',
    'name_1006',
    'go_id',
    'namespace_1003'
]


def download_biomart(gene_ids):
    import biomart

    server = biomart.BiomartServer('http://www.ensembl.org/biomart')
    data = server.datasets['hsapiens_gene_ensembl']

    res = data.search({
        'filters': {'ensembl_transcript_id_version': gene_ids},
        'attributes': columns,
    })
    assert res.ok

    with open(out_path, 'w') as io:
        io.write(res.text)


def select_genes(go_id, codes):
    restricted = df[df[columns.index('go_id')] == go_id]
    esn = columns.index('ensembl_transcript_id_version')
    restricted_genes = restricted[esn]

    rev_codes = codes.dropna().copy()
    rev_codes['barcode_id'] = rev_codes.index
    rev_codes.set_index('id', inplace=True)
    return rev_codes.loc[restricted_genes]


if __name__ == '__main__':
    codes = pd.read_csv(cb_path, skiprows=3, skipinitialspace=True)
    gene_ids = codes['id'].dropna().tolist()

    if not path.exists(out_path):
        download_biomart(gene_ids)

    df = pd.read_csv(out_path, sep='\t', header=None)
    go_argmax = df[columns.index('go_id')].value_counts().nlargest(1).index[0]
    assert 'GO:0005515' == go_argmax

    g = select_genes(go_argmax, codes)
    g.to_csv(sys.stdout)
