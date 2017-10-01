"""
    tests
    ~~~~~

    Tests for the :mod:`~scratchdir` module.
"""

import io
import os
import pytest
import shutil

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

import scratchdir


def is_file_like_obj(obj):
    """
    Helper function to check that the given object implements all public methods of the
    :class:`~io.IOBase` abstract class.
    """
    return all((hasattr(obj, name) for name in dir(io.IOBase) if not name.startswith('_')))


def is_pardir(pardir, subdir):
    """
    Helper function to check if the given path is a parent of another.
    """
    return pathlib.Path(pardir) in pathlib.Path(subdir).parents


@pytest.fixture(scope='function')
def scratch_dir(tmpdir):
    """
    Fixture that yields a :class:`~scratchdir.ScratchDir` instance with a root directory
    that is unique to each test invocation.
    """
    return scratchdir.ScratchDir(root=tmpdir.strpath)


@pytest.fixture(scope='function')
def active_scratch_dir(scratch_dir):
    """
    Fixture that yields a :class:`~scratchdir.ScratchDir` instance that has already performed
    the setup process and is active.
    """
    with scratch_dir:
        yield scratch_dir


def test_scratch_enter_calls_setup(scratch_dir, mocker):
    """
    Assert that :meth:`~scratchdir.ScratchDir.__enter__` calls :meth:`~scratchdir.ScratchDir.setup`.
    """
    with mocker.patch.object(scratch_dir, 'setup', wraps=scratch_dir.setup):
        with scratch_dir:
            assert scratch_dir.setup.called


def test_scratch_exit_calls_teardown(scratch_dir, mocker):
    """
    Assert that :meth:`~scratchdir.ScratchDir.__exit__` calls :meth:`~scratchdir.ScratchDir.teardown`.
    """
    with mocker.patch.object(scratch_dir, 'teardown', wraps=scratch_dir.teardown):
        with scratch_dir:
            pass
        assert scratch_dir.teardown.called


def test_scratch_is_not_active_when_wd_not_set(scratch_dir):
    """
    Assert that :prop:`~scratchdir.ScratchDir.active` is `False` when the
    working directory is not set.
    """
    scratch_dir.wd = None
    assert not scratch_dir.is_active


def test_scratch_is_not_active_when_wd_does_not_exist(active_scratch_dir, mocker):
    """
    Assert that an active :prop:`~scratchdir.ScratchDir.active` is `False` when the
    working directory does not exist.
    """
    assert active_scratch_dir.is_active
    with mocker.patch('os.path.exists', return_value=False):
        assert not active_scratch_dir.is_active


def test_scratch_is_not_active_when_setup_not_called(scratch_dir):
    """
    Assert that a :prop:`~scratchdir.ScratchDir.is_active` is `False` when
    :meth:`~scratchdir.ScratchDir.setup` has not been called.
    """
    assert not scratch_dir.is_active


def test_scratch_is_active_when_inside_context_manager(scratch_dir):
    """
    Assert that a :prop:`~scratchdir.ScratchDir.is_active` is `True` when
    the :meth:`~scratchdir.ScratchDir.__enter__` is called.
    """
    assert not scratch_dir.is_active
    with scratch_dir:
        assert scratch_dir.is_active


def test_scratch_is_not_active_after_context_manager(scratch_dir):
    """
    Assert that a :prop:`~scratchdir.ScratchDir.is_active` is `False` after
    the :meth:`~scratchdir.ScratchDir.__exit__` is called.
    """
    with scratch_dir:
        pass
    assert not scratch_dir.is_active


def test_scratch_setup_assigns_wd(scratch_dir):
    """
    Assert that :attr:`~scratchdir.ScratchDir.wd` is set after :meth:`~scratchdir.ScratchDir.setup` is called.
    """
    with scratch_dir:
        assert scratch_dir.wd is not None


def test_scratch_teardown_unassigns_wd(scratch_dir):
    """
    Assert that :attr:`~scratchdir.ScratchDir.wd` is not set after :meth:`~scratchdir.ScratchDir.teardown` is called.
    """
    with scratch_dir:
        pass
    assert scratch_dir.wd is None


def test_scratch_teardown_removes_files(scratch_dir, mocker):
    """
    Assert that :func:`~shutil.rmtree` is called when :func:`~scratchdir.ScratchDir.teardown` is called.
    """
    with mocker.patch('shutil.rmtree'):
        with scratch_dir:
            pass
        assert shutil.rmtree.called


@pytest.mark.parametrize('method_name', [
    'teardown',
    'child',
    'file',
    'named',
    'spooled',
    'secure',
    'directory',
    'filename',
    'join',
    'TemporaryFile',
    'NamedTemporaryFile',
    'SpooledTemporaryFile',
    'mkstemp',
    'mkdtemp'
])
def test_scratch_methods_raise_when_not_active(scratch_dir, method_name):
    """
    Assert that expected methods on the :class:`~scratchdir.ScratchDir` class raise a
    :class:`~scratchdir.ScratchDirInactiveError` exception when called while the instance is not active.
    """
    method = getattr(scratch_dir, method_name)
    with pytest.raises(scratchdir.ScratchDirInactiveError):
        assert method()


@pytest.mark.parametrize('method_name', [
    'file',
    'named',
    'secure',
    'TemporaryFile',
    'NamedTemporaryFile',
    'mkstemp'
])
def test_scratch_methods_given_unknown_subdir_raise(active_scratch_dir, method_name):
    """
    Assert that methods on :class:`~scratchdir.ScratchDir` that support a `dir` parameter will raise
    a :class:`~FileNotFoundError` when the dir does not exist.
    """
    method = getattr(active_scratch_dir, method_name)
    with pytest.raises(FileNotFoundError):
        assert method(dir='foo')


def test_scratch_child_returns_scratch_dir_instance(active_scratch_dir):
    """
    Assert that :meth:`~scratchdir.ScratchDir.child` returns a :class:`~scratchdir.ScratchDir` instance.
    """
    assert isinstance(active_scratch_dir.child(), scratchdir.ScratchDir)


def test_scratch_child_wd_is_within_parent_wd(active_scratch_dir):
    """
    Assert that :meth:`~scratchdir.ScratchDir.child` returns a :class:`~scratchdir.ScratchDir` instance
    whose working directory is a subdirectory of the working directory of the parent instance.
    """
    with active_scratch_dir.child() as child:
        assert is_pardir(active_scratch_dir.wd, child.wd)


@pytest.mark.parametrize('method_name', [
    'file',
    'named',
    'TemporaryFile',
    'NamedTemporaryFile'
])
def test_scratch_file_supports_file_obj_interface(active_scratch_dir, method_name):
    """
    Assert that methods of :class:`~scratchdir.ScratchDir` that are expected to return file-like objects
    do so and these objects implement, atleast, the :class:`~io.IOBase` interface.
    """
    method = getattr(active_scratch_dir, method_name)
    assert is_file_like_obj(method())


def test_scratch_secure_returns_fd_and_name_by_default(active_scratch_dir):
    """
    Assert that :meth:`~scratchdir.ScratchDir` returns a two item tuple containing the file descriptor
    and filename of the newly created temporary file.
    """
    result = active_scratch_dir.secure()
    assert isinstance(result, tuple)
    assert isinstance(result[0], int)
    assert isinstance(result[1], str)
    assert os.path.exists(result[1])


def test_scratch_secure_returns_only_name_on_toggle(active_scratch_dir):
    """
    Assert that :meth:`~scratchdir.ScratchDir` returns a :class:`str` containing the filename when
    configured to do so.
    """
    result = active_scratch_dir.secure(return_fd=False)
    assert isinstance(result, str)
    assert os.path.exists(result)
