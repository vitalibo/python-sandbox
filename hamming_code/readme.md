# Hamming Code

Hamming code is a linear error-correcting code that encodes data by adding parity bits. The code is capable of detecting
and correcting single-bit errors. The code is named after Richard Hamming, who introduced it in 1950.

## Usage

```python
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

```text
Data: [0 0 1 1 1 0 0 0 1 0 0]
Encoded: [1 0 0 1 0 1 1 0 1 0 0 0 1 0 0]
Corrupted: [1 0 0 1 0 0 1 0 1 0 0 0 1 0 0]
Decoded: [0 0 1 1 1 0 0 0 1 0 0]
Error: 5
```
