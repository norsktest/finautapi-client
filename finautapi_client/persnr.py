def generate_test_persnrs():
    """Generate 40 valid Norwegian D-numbers for testing purposes.

    Returns list of 40 valid 11-digit D-numbers (personnummer) as strings.
    D-numbers are test identifiers with day+40 in the first two digits.
    """
    import datetime

    # Weight vectors for MOD11 control digit calculation
    VEKT1 = [3, 7, 6, 1, 8, 9, 4, 5, 2, 1, 0]
    VEKT2 = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2, 1]

    def multiply_reduce(avec, bvec):
        return sum(a * b for a, b in zip(avec, bvec))

    def calc_parity(ppnr):
        """Add two control digits to 9-digit base."""
        # First control digit
        digits = [int(v) for v in ppnr[:9]]
        val1 = 11 - multiply_reduce(digits, VEKT1[:9]) % 11
        if val1 >= 10:
            return None
        ppnr10 = ppnr + str(val1)

        # Second control digit
        digits = [int(v) for v in ppnr10]
        val2 = 11 - multiply_reduce(digits, VEKT2[:10]) % 11
        if val2 >= 10:
            return None
        return ppnr10 + str(val2)

    def is_valid(pnr):
        """Verify both control digits."""
        digits = [int(v) for v in pnr]
        return (multiply_reduce(digits, VEKT1) % 11 == 0 and
                multiply_reduce(digits, VEKT2) % 11 == 0)

    # Date: 25 years ago
    day = datetime.date.fromordinal(
        datetime.date.today().toordinal() - 25 * 365)
    datepart = f'{day.day + 40:02}{day.month:02}{day.year % 100:02}'

    # Generate all valid D-numbers for this date (even individ numbers = female)
    result = []
    for inr in range(0, 1000, 2):
        pnr = calc_parity(f'{datepart}{inr:03}')
        if pnr and is_valid(pnr):
            result.append(pnr)

    return result[-40:]  # Return last 40


if __name__ == "__main__":
    for p in generate_test_persnrs():
        print(p)