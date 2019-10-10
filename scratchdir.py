"""
    scratchdir
    ~~~~~~~~~~

    Context manager used to maintain your temporary directories/files.
"""
import functools
import os
import shutil
import sys
import tempfile
import typing
import uuid


__all__ = ['ScratchDirError', 'ScratchDirInactiveError', 'ScratchDir']


# Prefix/suffix defaults in stdlib change starting in Python 3.5
if sys.version_info >= (3, 5):
    DEFAULT_PREFIX = None
    DEFAULT_SUFFIX = None
else:
    DEFAULT_PREFIX = 'tmp'
    DEFAULT_SUFFIX = ''

# Default working directory value.
DEFAULT_WD = ''


class ScratchDirError(Exception):
    """
    Base exception used for all :mod:`scratchdir` related errors.
    """


class ScratchDirInactiveError(ScratchDirError):
    """
    Exception raised when incorrectly attempting to perform an action against a :class:`~scratchdir.ScratchDir`
    that is not active.
    """


def requires_activation(func):
    """
    Decorate a bound method on the :class:`~scratchdir.ScratchDir` to assert that it is active before
    performing certain actions.
    """
    @functools.wraps(func)
    def decorator(self, *args, **kwargs):  # pylint: disable=missing-docstring
        if not self.is_active:
            raise ScratchDirInactiveError('ScratchDir must be active to perform this action')
        return func(self, *args, **kwargs)
    return decorator


class ScratchDir:
    """
    Represents a directory on disk within the default temporary directory that can be used to store context
    specific subdirectories and files.
    """

    def __init__(self, prefix: str = '', suffix: str = '.scratchdir', base: typing.Optional[str] = None,
                 root: typing.Optional[str] = tempfile.tempdir, wd: str = DEFAULT_WD) -> None:
        self.prefix = prefix
        self.suffix = suffix
        self.base = base
        self.root = root
        self.wd = wd

    def __enter__(self) -> 'ScratchDir':
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.teardown()

    @property
    def is_active(self) -> bool:
        """
        Check to see if the current scratch dir is active.

        A scratch dir is active if :meth:`~scratchdir.ScratchDir.setup` has been called and its
        working directory exists on disk.

        :return: Boolean indicating if the scratch dir is active or not
        :rtype: :class:`~bool`
        """
        return bool(self.wd) and os.path.exists(self.wd)

    def setup(self) -> None:
        """
        Setup the scratch dir by creating a temporary directory to become the root of all new temporary directories
        and files created by this instance.

        :return: Nothing
        :rtype: :class:`~NoneType`
        """
        tempfile.tempdir = self.root
        self.wd = self.wd or tempfile.mkdtemp(self.suffix, self.prefix, self.base)

    @requires_activation
    def teardown(self) -> None:
        """
        Teardown the scratch dir by deleting all directories and files within the scratch dir.

        :return: Nothing
        :rtype: :class:`~NoneType`
        """
        shutil.rmtree(self.wd)
        self.wd = DEFAULT_WD

    @requires_activation
    def child(self, prefix: str = '', suffix: str = '.scratchdir') -> 'ScratchDir':
        """
        Create a new :class:`~scratchdir.ScratchDir` instance whose working directory is a temporary directory
        within this scratch dir.

        :param prefix: (Optional) prefix of the temporary directory for this child scratch dir
        :type prefix: :class:`~str`
        :param suffix: (Optional) suffix of the temporary directory for this child scratch dir
        :type suffix: :class:`~str`
        :return: ScratchDir instance that is scoped within the current scratch dir
        :rtype: :class:`~scratchdir.ScratchDir`
        """
        return self.__class__(prefix, suffix, self.wd)

    @requires_activation
    def file(self, mode: str = 'w+b', buffering: int = -1, encoding: typing.Optional[str] = None,
             newline: typing.Optional[str] = None, suffix: typing.Optional[str] = DEFAULT_SUFFIX,
             prefix: typing.Optional[str] = DEFAULT_PREFIX, dir: typing.Optional[str] = None) -> typing.IO:
        """
        Create a new temporary file within the scratch dir.

        This returns the result of :func:`~tempfile.TemporaryFile` which returns a nameless, file-like object that
        will cease to exist once it is closed.

        :param mode: (Optional) mode to open the file with
        :type mode: :class:`~str`
        :param buffering: (Optional) size of the file buffer
        :type buffering: :class:`~int`
        :param encoding: (Optional) encoding to open the file with
        :type encoding: :class:`~str` or :class:`~NoneType`
        :param newline: (Optional) newline argument to open the file with
        :type newline: :class:`~str` or :class:`~NoneType`
        :param suffix: (Optional) filename suffix
        :type suffix: :class:`~str` or :class:`~NoneType`
        :param prefix: (Optional) filename prefix
        :type prefix: :class:`~str` or :class:`~NoneType`
        :param dir: (Optional) relative path to directory within the scratch dir where the file should exist
        :type dir: :class:`~str` or :class:`~NoneType`
        :return: file-like object as returned by :func:`~tempfile.TemporaryFile`
        :rtype: :class:`~_io.BufferedRandom`
        """
        return tempfile.TemporaryFile(mode, buffering, encoding, newline,
                                      suffix, prefix, self.join(dir))

    @requires_activation
    def named(self, mode: str = 'w+b', buffering: int = -1, encoding: typing.Optional[str] = None,
              newline: typing.Optional[str] = None, suffix: typing.Optional[str] = DEFAULT_SUFFIX,
              prefix: typing.Optional[str] = DEFAULT_PREFIX, dir: typing.Optional[str] = None,
              delete: bool = True) -> typing.IO:
        """
        Create a new named temporary file within the scratch dir.

        This returns the result of :func:`~tempfile.NamedTemporaryFile` which returns a named, file-like object that
        will cease to exist once it is closed unless `delete` is set to `False`.

        :param mode: (Optional) mode to open the file with
        :type mode: :class:`~str`
        :param buffering: (Optional) size of the file buffer
        :type buffering: :class:`~int`
        :param encoding: (Optional) encoding to open the file with
        :type encoding: :class:`~str` or :class:`~NoneType`
        :param newline: (Optional) newline argument to open the file with
        :type newline: :class:`~str` or :class:`~NoneType`
        :param suffix: (Optional) filename suffix
        :type suffix: :class:`~str` or :class:`~NoneType`
        :param prefix: (Optional) filename prefix
        :type prefix: :class:`~str` or :class:`~NoneType`
        :param dir: (Optional) relative path to directory within the scratch dir where the file should exist
        :type dir: :class:`~str` or :class:`~NoneType`
        :param delete: (Optional) flag to indicate if the file should be deleted from disk when it is closed
        :type delete: :class:`~bool`
        :return: file-like object as returned by :func:`~tempfile.NamedTemporaryFile`
        :rtype: :class:`~_io.TemporaryFileWrapper`
        """
        return tempfile.NamedTemporaryFile(mode, buffering, encoding, newline,
                                           suffix, prefix, self.join(dir), delete)

    @requires_activation
    def spooled(self, max_size: int = 0, mode: str = 'w+b', buffering: int = -1,
                encoding: typing.Optional[str] = None, newline: typing.Optional[str] = None,
                suffix: typing.Optional[str] = DEFAULT_SUFFIX, prefix: typing.Optional[str] = DEFAULT_PREFIX,
                dir: typing.Optional[str] = None) -> typing.IO:
        """
        Create a new spooled temporary file within the scratch dir.

        This returns a :class:`~tempfile.SpooledTemporaryFile` which is a specialized object that wraps a
        :class:`StringIO`/:class:`BytesIO` instance that transparently overflows into a file on the disk once it
        reaches a certain size.

        By default, a spooled file will never roll over to disk.

        :param max_size: (Optional) max size before the in-memory buffer rolls over to disk
        :type max_size: :class:`~int`
        :param mode: (Optional) mode to open the file with
        :type mode: :class:`~str`
        :param buffering: (Optional) size of the file buffer
        :type buffering: :class:`~int`
        :param encoding: (Optional) encoding to open the file with
        :type encoding: :class:`~str`
        :param newline: (Optional) newline argument to open the file with
        :type newline: :class:`~str` or :class:`~NoneType`
        :param suffix: (Optional) filename suffix
        :type suffix: :class:`~str` or :class:`~NoneType`
        :param prefix: (Optional) filename prefix
        :type prefix: :class:`~str` or :class:`~NoneType`
        :param dir: (Optional) relative path to directory within the scratch dir where the file should exist
        :type dir: :class:`~bool`
        :return: SpooledTemporaryFile instance
        :rtype: :class:`~tempfile.SpooledTemporaryFile`
        """
        return tempfile.SpooledTemporaryFile(max_size, mode, buffering, encoding,
                                             newline, suffix, prefix, self.join(dir))

    @requires_activation
    def secure(self, suffix: typing.Optional[str] = DEFAULT_SUFFIX,
               prefix: typing.Optional[str] = DEFAULT_PREFIX, dir: typing.Optional[str] = None,
               text: bool = False, return_fd: bool = True) -> typing.Union[str, typing.Tuple[int, str]]:
        """
        Create a new temporary file within the scratch dir in the most secure manner possible
        with the lowest possibility of race conditions during creation.

        This returns the result of :func:`~tempfile.mkstemp` which returns the file descriptor and filename to
        the newly created temporary file.

        By default, the caller is only passed back the file descriptor and filename unless
        `return_fd` is set to `False`.

        :param suffix: (Optional) filename suffix
        :type suffix: :class:`~str` or :class:`~NoneType`
        :param prefix: (Optional) filename prefix
        :type prefix: :class:`~str` or :class:`~NoneType`
        :param dir: (Optional) relative path to directory within the scratch dir where the file should exist
        :type dir: :class:`~str` or :class:`~NoneType`
        :param text: (Optional) flag to indicate if the file should be opened in text mode instead of binary
        :type text: :class:`~bool`
        :param return_fd: (Optional) flag to indicate if the file descriptor should also be returned
        :type text: :class:`~bool`
        :return: String representing the temporary file name or Tuple of file descriptor and filename
        :rtype: :class:`~str` or :class:`~tuple`
        """
        fd, filename = tempfile.mkstemp(suffix, prefix, self.join(dir), text)
        if return_fd:
            return fd, filename

        os.close(fd)
        return filename

    @requires_activation
    def directory(self, suffix: typing.Optional[str] = DEFAULT_SUFFIX,
                  prefix: typing.Optional[str] = DEFAULT_PREFIX, dir: bool = None) -> str:
        """
        Creates a new temporary directory within the scratch dir in the most secure manner possible and no
        chance of race conditions.

        This returns the result of :func:`~tempfile.mkdtemp` which returns the fully qualified path to the directory.

        :param suffix: (Optional) directory name suffix
        :type suffix: :class:`~str` or :class:`~NoneType`
        :param prefix: (Optional) directory name prefix
        :type prefix: :class:`~str` or :class:`~NoneType`
        :param dir: (Optional) relative path to directory within the scratch dir where the directory should exist
        :type dir: :class:`~str` or :class:`~NoneType`
        :return: Path on disk where new directory exists
        :rtype: :class:`~str`
        """
        return tempfile.mkdtemp(suffix, prefix, self.join(dir))

    @requires_activation
    def filename(self, suffix: typing.Optional[str] = DEFAULT_SUFFIX,
                 prefix: typing.Optional[str] = DEFAULT_PREFIX) -> str:
        """
        Create a filename that is unique within the scratch dir.

        This returns the fully qualified path to the unique filename within the scratch dir but does not create
        a temporary file for that location.

        :param suffix: (Optional) filename suffix
        :type suffix: :class:`~str` or :class:`~NoneType`
        :param prefix: (Optional) filename prefix
        :type prefix: :class:`~str` or :class:`~NoneType`
        :return: Path in scratch dir for unique filename
        :rtype: :class:`~str`
        """
        prefix = prefix if prefix is not None else ''
        suffix = suffix if suffix is not None else ''
        return self.join(''.join((prefix, str(uuid.uuid4()), suffix)))

    @requires_activation
    def join(self, *paths: str) -> str:
        """
        Builds a fully qualified path to the given location relative to the scratch dir.

        :param paths: One or more paths to join
        :type paths: :class:`~tuple of `:class:`~str`
        :return: Fully qualified path within scratch dir
        :rtype: :class:`~str`
        """
        return os.path.join(self.wd, *(str(p) for p in paths if p is not None))

    # Aliases
    TemporaryFile = file
    NamedTemporaryFile = named
    SpooledTemporaryFile = spooled
    mkstemp = secure
    mkdtemp = directory
