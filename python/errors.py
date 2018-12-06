import click
import numpy as np
from reader import load_merfish, read_codebook


@click.command()
@click.argument("MERFISH", type=click.Path())
@click.argument("CODEBOOK", type=click.Path())
def estimate_errors(merfish: str, codebook: str):
    """Calculate field-of-view dimensions and overlap.
    """
    data = load_merfish(merfish)[['barcode', 'error_bit']]
    num_records = data.shape[0]
    error_bits = np.array(data['error_bit'], dtype=np.uint32)
    barcodes = data['barcode']

    correction = 1 << (error_bits - 1)  # error_bit == 0 → no error, error_bit == n → error at position (n-1)
    correction[error_bits == 0] = 0
    uncorrected_barcodes = barcodes ^ correction
    num_corrected_barcodes = np.count_nonzero(error_bits)
    assert num_corrected_barcodes == np.sum(uncorrected_barcodes != barcodes)

    one_to_zero_errors = (barcodes & correction)
    zero_to_one_errors = ((~barcodes) & correction)

    print("One → Zero errors (for each index):")
    sel = (1 << np.arange(0, 16)).reshape((-1, 1))
    print('\n'.join(map(str, zip(range(16), np.sum(one_to_zero_errors == sel, axis=1) / num_records))))
    # for i in range(16):
    #     print(f"{i}: {np.sum(one_to_zero_errors == (1 << i)) / num_records}")

    print()
    print("Zero → One errors (for each index):")
    print('\n'.join(map(str, zip(range(16), np.sum(zero_to_one_errors == sel, axis=1) / num_records))))
    # for i in range(16):
    #     print(f"{i}: {np.sum(zero_to_one_errors == (1 << i)) / num_records}")

    codes = read_codebook(codebook)[['name', 'barcode']]
    blanks = codes[codes['name'].str.startswith('Blank-')]
    blank_barcodes_str = list(map(bin, blanks['barcode'].values))
    blank_barcodes = blanks['barcode'].values.reshape((-1, 1))

    print()
    print(f"Assigned blank counts (pre-correction):\n"
          f"{dict(zip(blank_barcodes_str, np.sum(uncorrected_barcodes == blank_barcodes, axis=1)))}")
    print()
    print(f"Assigned blank counts (post-correction):\n"
          f"{dict(zip(blank_barcodes_str, np.sum(barcodes == blank_barcodes, axis=1)))}")


if __name__ == "__main__":
    estimate_errors()
