"""
base 36 encoding/decoding taken from wikipedia sample code
http://en.wikipedia.org/wiki/Base_36#Python_Conversion_Code
"""


def encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """
    Converts an integer to a base36 string.

    :type number: int or long
    :rtype: str
    """

    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')

    if 0 <= number <= 9:
        return alphabet[number]

    base36 = ''
    sign = ''

    if number < 0:
        sign = '-'
        number = -number

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return sign + base36


def decode(number):
    """
    Converts a base36 string to an integer.

    :type number: str
    :rtype: int
    """
    return int(number, 36)
