.. code-block:: python

	def file_exists(filepath: str, raise_exception: bool = True) -> bool:
    """This checks if the file exists, and, in function of a boolean parameter, raises an exception if it doesn't

    Parameters
    ----------
    filepath : str
        the filepath to check the existence of
    raise_exception : bool, optional
        whether to raise an exception, by default True

    Returns
    -------
    bool
        whether the file exists

    Raises
    ------
    FileNotFoundError
        error raised if the file doesn't exist

    See Also
    --------
    similar_filenames : to find the most similar filenames to a filename

    Examples
    --------

    .. code-block:: python

        name = "file.txt"
        exists = file_exists(name)

    """
    filepath = os.path.abspath(filepath)
    exists = os.path.exists(filepath)
    if exists:
        return True
    else:
        if raise_exception:
            raise FileNotFoundError(f"The file {filepath} doesn't exist")
        else:
            return False
