"""
    tests
    ~~~~~

    Tests for the :mod:`~scratchdir` module.
"""

import pytest
import shutil

import scratchdir


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
