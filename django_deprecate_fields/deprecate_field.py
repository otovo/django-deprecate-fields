import logging
import sys
import warnings

logger = logging.getLogger(__file__)


class DeprecatedField(object):
    """
    Descriptor class for deprecated fields. Do not use directly, use the
    deprecate_field function instead.
    """

    def __init__(self, val):
        self.val = val

    def _get_name(self, obj):
        """
        Try to find this field's name in the model class
        """
        return next(
            (k for k, v in type(obj).__dict__.items() if v is self), "<unknown>"
        )

    def __get__(self, obj, type=None):
        msg = f"accessing deprecated field {obj.__class__.__name__}.{self._get_name(obj)}"
        warnings.warn(msg, DeprecationWarning, stacklevel=2)
        logger.warning(msg)
        return self.val if not callable(self.val) else self.val()

    def __set__(self, obj, val):
        msg = f"writing to deprecated field {obj.__class__.__name__}.{self._get_name(obj)}"
        warnings.warn(msg, DeprecationWarning, stacklevel=2)
        logger.warning(msg)
        self.val = val


def deprecate_field(field_instance, return_instead=None):
    """
    Can be used in models to delete a Field in a Backwards compatible manner.
    The process for deleting old model Fields is:
    1. Mark a field as deprecated by wrapping the field with this function
    2. Wait until (1) is deployed to every relevant server/branch
    3. Delete the field from the model.

    For (1) and (3) you need to run ./manage.py makemigrations:
    :param field_instance: The field to deprecate
    :param return_instead: A value or function that
    the field will pretend to have
    """
    if not set(sys.argv) & {"makemigrations", "migrate", "showmigrations"}:
        return DeprecatedField(return_instead)

    field_instance.null = True
    return field_instance
