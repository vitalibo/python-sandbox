# Hamming Code

Hamming code is a linear error-correcting code that encodes data by adding parity bits. The code is capable of detecting
and correcting single-bit errors and detecting two-bit errors. The code was developed by Richard Hamming in 1950. The
code is widely used in computer memory systems, data transmission, and error detection and correction.

## Usage

The following example demonstrates how to encode and decode data using Hamming code.

```python
import numpy as np
from hamming_code import encode, decode

data = np.random.randint(0, 2, 11)
print(f"Data: {data}")

code = encode(data)
print(f"Encoded: {code}")

code[np.random.randint(0, len(code))] ^= 1
print(f"Corrupted: {code}")

error, decoded = decode(code)
print(f"Decoded: {decoded}")
print(f"Error: {error}")
assert np.array_equal(data, decoded)
```

The output of the example is as follows:

```text
Data: [0 0 1 0 1 1 1 1 1 1 0]
Encoded: [1 0 0 0 0 1 0 0 1 1 1 1 1 1 0 0]
Corrupted: [1 0 0 0 0 1 0 0 1 0 1 1 1 1 0 0]
Decoded: [0 0 1 0 1 1 1 1 1 1 0]
Error: 9
```

Visual representation of the example:

Encoding:

| Bit Position  | 1     | 2     | 3  | 4     | 5  | 6  | 7  | 8     | 9  | 10 | 11 | 12 | 13 | 14  | 15  | 16    |
|---------------|-------|-------|----|-------|----|----|----|-------|----|----|----|----|----|-----|-----|-------|
| Position Name | P1    | P2    | D1 | P3    | D2 | D3 | D4 | P4    | D5 | D6 | D7 | D8 | D9 | D10 | D11 | Pn-1  |
| Hamming Code  | 1     | 0     | 0  | 0     | 0  | 1  | 0  | 0     | 1  | 1  | 1  | 1  | 1  | 1   | 0   | 0     |
| Data Bits     |       |       | 0  |       | 0  | 1  | 0  |       | 1  | 1  | 1  | 1  | 1  | 1   | 0   |       |
| P1            | **1** |       | 0  |       | 0  |    | 0  |       | 1  |    | 1  |    | 1  |     | 0   |       |
| P2            |       | **0** | 0  |       |    | 1  | 0  |       |    | 1  | 1  |    |    | 1   | 0   |       |
| P3            |       |       |    | **0** | 0  | 1  | 0  |       |    |    |    | 1  | 1  | 1   | 0   |       |
| P4            |       |       |    |       |    |    |    | **0** | 1  | 1  | 1  | 1  | 1  | 1   | 0   |       |
| Pn-1          | 1     | 0     | 0  | 0     | 0  | 1  | 0  | 0     | 1  | 1  | 1  | 1  | 1  | 1   | 0   | **0** |

- `P1` = `D1 xor D2 xor D4 xor D5 xor D7 xor D8 xor D10 xor D11` = `1 xor 0 xor 0 xor 1 xor 0 xor 0 xor 1 xor 0` = `1`
- `P2` = `D1 xor D3 xor D4 xor D6 xor D7 xor D9 xor D10 xor D11` = `1 xor 0 xor 0 xor 0 xor 0 xor 1 xor 1 xor 0` = `0`
- `P3` = `D2 xor D3 xor D4 xor D8 xor D9 xor D10 xor D11` = `0 xor 1 xor 0 xor 1 xor 1 xor 1 xor 0` = `0`
- `P4` = `D5 xor D6 xor D7 xor D8 xor D9 xor D10 xor D11` = `1 xor 1 xor 1 xor 1 xor 1 xor 1 xor 0` = `0`
- `Pn-1` = `P1 xor P2 xor D1 xor P3 xor D2 xor D3 xor D4 xor P4 xor D5 xor D6 xor D7 xor D8 xor D9 xor D10 xor D11` = `1 xor 0  xor 0 xor 0 xor 0 xor 1 xor 0 xor 0 xor 1 xor 1 xor 1 xor 1 xor 1 xor 1 xor 0` = `0`

Decoding:

| Bit Position  | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  | 10 | 11 | 12 | 13 | 14  | 15  | 16   | Error |
|---------------|----|----|----|----|----|----|----|----|----|----|----|----|----|-----|-----|------|-------|
| Position Name | P1 | P2 | D1 | P3 | D2 | D3 | D4 | P4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | Pn-1 |       |
| Hamming Code  | 1  | 0  | 0  | 0  | 0  | 1  | 0  | 0  | 1  | 0  | 1  | 1  | 1  | 1   | 0   | 0    |       | 
| P1            | 1  |    | 0  |    | 0  |    | 0  |    | 1  |    | 1  |    | 1  |     | 0   |      | 0     |
| P2            |    | 0  | 0  |    |    | 1  | 0  |    |    | 0  | 1  |    |    | 1   | 0   |      | 1     |
| P3            |    |    |    | 0  | 0  | 1  | 0  |    |    |    |    | 1  | 1  | 1   | 0   |      | 0     |
| P4            |    |    |    |    |    |    |    | 0  | 1  | 0  | 1  | 1  | 1  | 1   | 0   |      | 1     |
| Pn-1          | 1  | 0  | 0  | 0  | 0  | 1  | 0  | 0  | 1  | 0  | 1  | 1  | 1  | 1   | 0   | 0    |       |

- `P1 xor D1 xor D2 xor D4 xor D5 xor D7 xor D8 xor D10 xor D11` = `1 xor 1 xor 0 xor 0 xor 1 xor 0 xor 0 xor 1 xor 0` = `0`
- `P2 xor D1 xor D3 xor D4 xor D6 xor D7 xor D9 xor D10 xor D11` = `0 xor 1 xor 0 xor 0 xor 0 xor 1 xor 0 xor 1 xor 0` = `1`
- `P3 xor D2 xor D3 xor D4 xor D8 xor D9 xor D10 xor D11` = `0 xor 0 xor 1 xor 0 xor 1 xor 1 xor 1 xor 0` = `0`
- `P4 xor D5 xor D6 xor D7 xor D8 xor D9 xor D10 xor D11` = `0 xor 1 xor 0 xor 1 xor 1 xor 1 xor 1 xor 0` = `1`

Error Position = `P4 P3 P2 P1` = `1 0 1 0` = `0b1010` = `10` or `9 (0-indexed)`

- `P1 xor P2 xor D1 xor P3 xor D2 xor D3 xor D4 xor P4 xor D5 xor D6 xor D7 xor D8 xor D9 xor D10 xor D11` = `1 xor 0  xor 0 xor 0 xor 0 xor 1 xor 0 xor 0 xor 1 xor 0 xor 1 xor 1 xor 1 xor 1 xor 0` = `1`

Parity Check Bit (Pn-1) = `1`

- if `error = 0` and `parity_check = 0`, no error occurred;
- if `error > 0` and `parity_check = 1`, a single error occurred that can be corrected;
- if `error > 0` and `parity_check = 0`, a double error occurred that cannot be corrected;
- if `error = 0` and `parity_check = 1`, a single error occurred in the Pn+1 bit, which can be corrected.

In this example, the error is `10` and the parity check bit is `1`, which means a single error occurred that can be
corrected. To correct the error, the bit at position `10` is flipped from `0` to `1`.
