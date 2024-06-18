import itertools
import unittest

import numpy as np

from hamming_code import encode, decode


class TestHammingCodeNumpy(unittest.TestCase):

    def setUp(self):
        self.samples = [np.array(i) for i in itertools.product([0, 1], repeat=8)]

    def test_no_error(self):
        for data in self.samples:
            with self.subTest(msg=data):
                code = encode(data)

                error, decoded = decode(code)

                assert error == -1
                assert np.array_equal(data, decoded)

    def test_single_error(self):
        for data in self.samples:
            for error in range(len(data)):
                with self.subTest(msg=f'{data} with error at {error}'):
                    code = encode(data)

                    code[error] ^= 1

                    error, decoded = decode(code)

                    assert error == error
                    assert np.array_equal(data, decoded)

    def test_double_error(self):
        for data in self.samples:
            for error1 in range(len(data) - 1):
                for error2 in range(error1 + 1, len(data)):
                    with self.subTest(msg=f'{data} with errors at {error1} and {error2}'):
                        code = encode(data)

                        code[error1] ^= 1
                        code[error2] ^= 1

                        with self.assertRaises(ValueError):
                            decode(code)


if __name__ == '__main__':
    unittest.main()
