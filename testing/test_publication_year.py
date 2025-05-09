import unittest
from datetime import datetime


def is_valid_author_dates(birth_date, date_of_death):
    """
    Validates the birth date and death date of an author.
    Ensures birth date is not in the future and death date is after birth date (if applicable).
    """
    today = datetime.today().date()


    if birth_date > today:
        return False, "Birth date cannot be in the future."


    if date_of_death:
        if date_of_death > today:
            return False, "Death date cannot be in the future."
        if date_of_death < birth_date:
            return False, "Death date cannot be before birth date."

    return True, ""


class TestAuthorDateValidation(unittest.TestCase):
    """
    Test the validation of author dates (birth date and death date).
    """

    def test_birth_date_in_future(self):
        """Test if birth date is in the future."""
        future_birth_date = datetime(2050, 1, 1).date()
        valid, message = is_valid_author_dates(future_birth_date, None)
        self.assertFalse(valid)
        self.assertEqual(message, "Birth date cannot be in the future.")

    def test_death_date_in_future(self):
        """Test if death date is in the future."""
        birth_date = datetime(1900, 1, 1).date()
        future_death_date = datetime(2050, 1, 1).date()
        valid, message = is_valid_author_dates(birth_date, future_death_date)
        self.assertFalse(valid)
        self.assertEqual(message, "Death date cannot be in the future.")

    def test_death_date_before_birth_date(self):
        """Test if death date is before birth date."""
        birth_date = datetime(1900, 1, 1).date()
        death_date = datetime(1899, 12, 31).date()
        valid, message = is_valid_author_dates(birth_date, death_date)
        self.assertFalse(valid)
        self.assertEqual(message, "Death date cannot be before birth date.")

    def test_valid_dates_without_death(self):
        """Test valid birth date without death date."""
        birth_date = datetime(1900, 1, 1).date()
        valid, message = is_valid_author_dates(birth_date, None)
        self.assertTrue(valid)
        self.assertEqual(message, "")

    def test_valid_dates_with_death(self):
        """Test valid birth date and death date."""
        birth_date = datetime(1900, 1, 1).date()
        death_date = datetime(1980, 1, 1).date()
        valid, message = is_valid_author_dates(birth_date, death_date)
        self.assertTrue(valid)
        self.assertEqual(message, "")

    def test_death_date_after_birth_date(self):
        """Test if death date is after birth date."""
        birth_date = datetime(1900, 1, 1).date()
        death_date = datetime(2000, 1, 1).date()
        valid, message = is_valid_author_dates(birth_date, death_date)
        self.assertTrue(valid)
        self.assertEqual(message, "")


if __name__ == "__main__":
    unittest.main()
