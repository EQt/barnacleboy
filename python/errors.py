import click
import numpy as np
from reader import load_merfish


@click.command()
@click.argument("FILE", type=click.Path())
def error(file: str):
    """Calculate field-of-view dimensions and overlap.
    """
    data = load_merfish(file)[['barcode', 'error_bit']]
    num_records = data.shape[0]
    error_bits = np.array(data['error_bit'], dtype=np.uint32)
    barcodes = data['barcode']

    correction = 1 << (error_bits - 1)  # error_bit == 0 → no error, error_bit == n → error at position (n-1)
    correction[error_bits == 0] = 0
    corrected_barcodes = barcodes ^ correction
    num_corrected_barcodes = np.count_nonzero(error_bits)
    assert num_corrected_barcodes == np.sum(corrected_barcodes != barcodes)

    one_to_zero_errors = (barcodes & correction)
    zero_to_one_errors = ((~barcodes) & correction)

    print("One → Zero errors (for each index):")
    sel = (1 << np.arange(0, 16)).reshape((16, -1))
    print('\n'.join(map(str, zip(range(16), np.sum(one_to_zero_errors == sel, axis=1) / num_records))))
    # for i in range(16):
    #     print(f"{i}: {np.sum(one_to_zero_errors == (1 << i)) / num_records}")

    print()
    print("Zero → One errors (for each index):")
    print('\n'.join(map(str, zip(range(16), np.sum(zero_to_one_errors == sel, axis=1) / num_records))))
    # for i in range(16):
    #     print(f"{i}: {np.sum(zero_to_one_errors == (1 << i)) / num_records}")


if __name__ == "__main__":
    error()
