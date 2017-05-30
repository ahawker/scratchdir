"""
    scratchdir
    ~~~~~~~~~~

    Context manager used to maintain your temporary directories/files.
"""
import functools
import os
import shutil
import tempfile
import uuid


__all__ = ['ScratchSpace']


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
    def decorator(self, *args, **kwargs):
        if not self.is_active:
            raise ScratchDirInactiveError('ScratchDir must be active to perform this action')
        return func(self, *args, **kwargs)
    return decorator


class ScratchDir(object):
    """
    Represents a directory on disk within the default temporary directory that can be used to store context
    specific subdirectories and files.
    """

    def __init__(self, prefix='', suffix='.scratchdir', base=None, root=tempfile.tempdir, wd=None):
        self.prefix = prefix
        self.suffix = suffix
        self.base = base
        self.root = root
        self.wd = wd

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()

    @property
    def is_active(self):
        """
        Check to see if the current scratch dir is active.

        A scratch dir is active if :meth:`~scratchdir.ScratchDir.setup` has been called and its
        working directory exists on disk.

        :return: :class:`bool` indicating if the scratch dir is active or not
        """
        return bool(self.wd) and os.path.exists(self.wd)

    def setup(self):
        """
        Setup the scratch dir by creating a temporary directory to become the root of all new temporary directories
        and files created by this instance.
        """
        tempfile.tempdir = self.root
        self.wd = self.wd or tempfile.mkdtemp(self.suffix, self.prefix, self.base)

    @requires_activation
    def teardown(self):
        """
        Teardown the scratch dir by deleting all directories and files within the scratch dir.
        """
        shutil.rmtree(self.wd)
        self.wd = None

    @requires_activation
    def child(self, prefix='', suffix='.scratchdir'):
        """
        Create a new :class:`~scratchdir.ScratchDir` instance whose working directory is a temporary directory
        within this scratch dir.

        :param prefix: (Optional) prefix of the temporary directory for this child scratch dir
        :param suffix: (Optional) suffix of the temporary directory for this child scratch dir
        :return: :class:`~scratchdir.ScratchSpace` that is scoped within the current scratch dir
        """
        return self.__class__(prefix, suffix, self.wd)

    @requires_activation
    def file(self, mode='w+b', bufsize=-1, suffix='', prefix='tmp', dir=None):
        """
        Create a new temporary file within the scratch dir.

        This returns the result of :func:`~tempfile.TemporaryFile` which returns a nameless, file-like object that
        will cease to exist once it is closed.

        :param mode: (Optional) mode to open the file with
        :param bufsize: (Optional) size of the file buffer
        :param suffix: (Optional) filename suffix
        :param prefix: (Optional) filename prefix
        :param dir: (Optional) relative path to directory within the scratch dir where the file should exist
        :return: file-like object as returned by :func:`~tempfile.TemporaryFile`
        """
        return tempfile.TemporaryFile(mode, bufsize, suffix, prefix, self.join(dir))

    @requires_activation
    def named(self, mode='w+b', bufsize=-1, suffix='', prefix='tmp', dir=None, delete=True):
        """
        Create a new named temporary file within the scratch dir.

        This returns the result of :func:`~tempfile.NamedTemporaryFile` which returns a named, file-like object that
        will cease to exist once it is closed unless `delete` is set to `False`.

        :param mode: (Optional) mode to open the file with
        :param bufsize: (Optional) size of the file buffer
        :param suffix: (Optional) filename suffix
        :param prefix: (Optional) filename prefix
        :param dir: (Optional) relative path to directory within the scratch dir where the file should exist
        :param delete: (Optional) flag to indicate if the file should be deleted from disk when it is closed
        :return: file-like object as returned by :func:`~tempfile.NamedTemporaryFile`
        """
        return tempfile.NamedTemporaryFile(mode, bufsize, suffix, prefix, self.join(dir), delete)

    @requires_activation
    def spooled(self, max_size=0, mode='w+b', bufsize=-1, suffix='', prefix='tmp', dir=None):
        """
        Create a new spooled temporary file within the scratch dir.

        This returns a :class:`~tempfile.SpooledTemporaryFile` which is a specialized object that wraps a
        :class:`StringIO`/:class:`BytesIO` instance that transparently overflows into a file on the disk once it
        reaches a certain size.

        By default, a spooled file will never roll over to disk.

        :param max_size: (Optional) max size before the in-memory buffer rolls over to disk
        :param mode: (Optional) mode to open the file with
        :param bufsize: (Optional) size of the file buffer
        :param suffix: (Optional) filename suffix
        :param prefix: (Optional) filename prefix
        :param dir: (Optional) relative path to directory within the scratch dir where the file should exist
        :return: :class:`~tempfile.SpooledTemporaryFile` instance
        """
        return tempfile.SpooledTemporaryFile(max_size, mode, bufsize, suffix, prefix, self.join(dir))

    @requires_activation
    def secure(self, suffix='', prefix='tmp', dir=None, text=False, return_fd=True):
        """
        Create a new temporary file within the scratch dir in the most secure manner possible
        with the lowest possibility of race conditions during creation.

        This returns the result of :func:`~tempfile.mkstemp` which returns the file descriptor and filename to
        the newly created temporary file.

        By default, the caller is only passed back the file descriptor and filename unless
        `return_fd` is set to `False`.

        :param suffix: (Optional) filename suffix
        :param prefix: (Optional) filename prefix
        :param dir: (Optional) relative path to directory within the scratch dir where the file should exist
        :param text: (Optional) flag to indicate if the file should be opened in text mode instead of binary
        :param return_fd: (Optional) flag to indicate if the file descriptor should also be returned
        :return: :class:`~string` representing the temporary file name or :class:`~tuple` of fd and filename
        """
        fd, filename = tempfile.mkstemp(suffix, prefix, self.join(dir), text)
        if return_fd:
            return fd, filename

        os.close(fd)
        return filename

    @requires_activation
    def directory(self, suffix='', prefix='tmp', dir=None):
        """
        Creates a new temporary directory within the scratch dir in the most secure manner possible and no
        chance of race conditions.

        This returns the result of :func:`~tempfile.mkdtemp` which returns the fully qualified path to the directory.

        :param suffix: (Optional) directory name suffix
        :param prefix: (Optional) directory name prefix
        :param dir: (Optional) relative path to directory within the scratch dir where the directory should exist
        :return: :class:`~string` to path on disk where new directory exists
        """
        return tempfile.mkdtemp(suffix, prefix, self.join(dir))

    @requires_activation
    def filename(self, suffix='', prefix=''):
        """
        Create a filename that is unique within the scratch dir.

        This returns the fully qualified path to the unique filename within the scratch dir but does not create
        a temporary file for that location.

        :param suffix: (Optional) filename suffix
        :param prefix: (Optional) filename prefix
        :return: :class:`~string` to path in scratch dir for unique filename.
        """
        return self.join(''.join((prefix, str(uuid.uuid4()), suffix)))

    @requires_activation
    def join(self, *paths):
        """
        Builds a fully qualified path to the given location relative to the scratch dir.

        :param paths: One or more paths to join
        :return: :class:`~string` to path within scratch dir
        """
        return os.path.join(self.wd, *(str(p) for p in paths if p is not None))

    # Aliases
    mkstemp = secure
    mkdtemp = directory
