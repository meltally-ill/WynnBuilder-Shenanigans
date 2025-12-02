# everyone say thanks doctor seek for this code
class Base64:
    _digits_str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+-"
    _digits = list(_digits_str)
    _digits_map = {ch: i for i, ch in enumerate(_digits)}


    @staticmethod
    def to_int(digits_str: str) -> int:
        """Return an integer from a Base64 compatible string."""
        result = 0
        for char in digits_str:
            result = (result << 6) + Base64._digits_map[char]
        return result