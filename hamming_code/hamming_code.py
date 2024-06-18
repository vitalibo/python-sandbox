import numpy as np


def encode(data: np.ndarray) -> np.ndarray:
    """
    Encode data with Hamming code with single error correction and double error detection.

    :param data: numpy array with data to encode.
    :return: encoded numpy array.
    """

    parity_bits = 0
    while 2 ** parity_bits < len(data) + parity_bits + 1:
        parity_bits += 1

    n = len(data) + parity_bits + 1
    code = np.zeros(n, dtype=np.int8)

    mask = np.arange(n) + 1
    mask[-1] = 0
    code[mask & mask - 1 > 0] = data

    i = 1
    while i < n - 1:
        code[i - 1] = code[mask & i > 0].sum() & 1
        i = i << 1

    code[-1] = code.sum() & 1

    return code


def decode(code: np.ndarray) -> tuple[int, np.ndarray]:
    """
    Decode Hamming code with single error correction and double error detection.

    :param code: numpy array encoded with Hamming code.
    :return: tuple of error position and corrected data. If error is not found, return -1.
    :throws ValueError: if double error is detected.
    """

    mask = np.arange(len(code)) + 1
    mask[-1] = 0

    error = -1
    i = 1
    while i < len(code) - 1:
        error += i * (code[mask & i > 0].sum() & 1)
        i = i << 1

    parity = code.sum() & 1
    if error >= 0:
        if parity == 1:
            code[error] ^= 1
        else:
            raise ValueError("Double error detected")
    elif parity == 1:
        error = len(code) - 1

    return int(error), code[mask & mask - 1 > 0]
