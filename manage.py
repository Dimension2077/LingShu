#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # NOTE: Python modules cannot contain '-' in their name.
    # Use the importable Django project package instead.
    # Use assignment (not setdefault) so existing environment variables
    # like DJANGO_SETTINGS_MODULE=DM-AI.settings cannot override it.
    os.environ['DJANGO_SETTINGS_MODULE'] = 'LingShu_AI.settings'
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
