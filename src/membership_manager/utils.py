import random
import string
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def validateEmail( email ):
    try:
        validate_email( email )
        return True
    except ValidationError:
        return False

def stringcode_generator(size=4, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))
