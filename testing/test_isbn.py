import unittest
from app import is_valid_isbn, check_isbn13

class ISBNValidationTest(unittest.TestCase):
    def test_valid_isbn(self):
        """
        Test valid ISBN-13 formats.
        """
        valid_isbns = [
            "978-3-16-148410-0",
            "9783161484100",
            "978-0-306-40615-7",
        ]
        for isbn in valid_isbns:
            with self.subTest(isbn=isbn):
                self.assertTrue(is_valid_isbn(isbn), f"Failed for ISBN {isbn}")

    def test_invalid_isbn_length(self):
        """
        Test ISBNs with incorrect lengths.
        """
        invalid_isbns = [
            "978-3-16-148410",
            "978-3-16-148410-00",
        ]
        for isbn in invalid_isbns:
            with self.subTest(isbn=isbn):
                self.assertFalse(is_valid_isbn(isbn), f"Failed for ISBN {isbn}")

    def test_invalid_isbn_format(self):
        """
        Test ISBNs with invalid characters.
        """
        invalid_isbns = [
            "978-3-16-14841X-0",
            "978-3-16-148410-A",
            "978316148410X",
        ]
        for isbn in invalid_isbns:
            with self.subTest(isbn=isbn):
                self.assertFalse(is_valid_isbn(isbn), f"Failed for ISBN {isbn}")

    def test_isbn_check_digit(self):
        """
        Test ISBN-13 checksum calculation.
        """
        valid_isbns = [
            "978-3-16-148410-0",
            "978-0-306-40615-7",
        ]
        for isbn in valid_isbns:
            with self.subTest(isbn=isbn):
                self.assertTrue(check_isbn13(isbn.replace("-", "")), f"Failed for ISBN {isbn}")

if __name__ == '__main__':
    unittest.main()
