from os.path import dirname


def get_include():
    """Return the include directory for lazy.

    Returns
    -------
    include_dir : str
        The path to the include directory.
    """
    return dirname(__file__)
