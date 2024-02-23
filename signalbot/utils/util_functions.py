import re
from re import Match
from typing import Optional


def is_internal_id(internal_id: str) -> bool:
    """
    Check if the provided internal_id is valid.

    This function checks if the internal_id is not None and if it ends with an "=" sign. The function returns False
    if the internal_id is None, otherwise it returns True if the last character of the internal_id is "=".

    Args:
        internal_id (str): The internal_id to be checked.

    Returns:
        bool: True if the internal_id is not None and ends with "=", False otherwise.
    """
    if internal_id is None:
        return False
    return internal_id[-1] == '='


def is_phone_number(phone_number: str) -> bool:
    """
    Validates a phone number using regex.

    A valid phone number must start with a "+", followed by up to 15 digits.

    Args:
    phone_number (str): The phone number to validate.

    Returns:
    bool: True if the phone number is valid, False otherwise.
    """
    pattern = r'^\+[0-9]{1,15}$'

    if phone_number is None:
        return False
    return bool(re.match(pattern, phone_number))


def is_group_id(group_id: str) -> Optional[Match[str]]:
    """Check if group_id has the right format, e.g.

          random string                                              length 66
          ↓                                                          ↓
    group.OyZzqio1xDmYiLsQ1VsqRcUFOU4tK2TcECmYt2KeozHJwglMBHAPS7jlkrm=
    ↑                                                                ↑
    prefix                                                           suffix
    """
    if group_id is None:
        return None

    pattern = r'^group\.[a-zA-Z0-9]{59}=$'
    return re.match(pattern, group_id)
