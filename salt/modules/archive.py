'''
A module to wrap archive calls
'''

# Import salt libs
import salt._compat
from salt.utils import which as _which
import salt.utils.decorators as decorators

# TODO: Check that the passed arguments are correct

# Don't shadow built-in's.
__func_alias__ = {
    'zip_': 'zip'
}


def __virtual__():
    commands = ('tar', 'gzip', 'gunzip', 'zip', 'unzip', 'rar', 'unrar')
    # If none of the above commands are in $PATH this module is a no-go
    if not any(_which(cmd) for cmd in commands):
        return False
    return 'archive'


@decorators.which('tar')
def tar(options, tarfile, sources, cwd=None, template=None):
    '''
    Uses the tar command to pack, unpack, etc tar files

    CLI Example::

        salt '*' archive.tar cjvf /tmp/tarfile.tar.bz2 /tmp/file_1,/tmp/file_2

    The template arg can be set to 'jinja' or another supported template
    engine to render the command arguments before execution.
    For example::

        salt '*' archive.tar template=jinja cjvf /tmp/salt.tar.bz2 \
                {{grains.saltpath}}

    '''
    if isinstance(sources, salt._compat.string_types):
        sources = [s.strip() for s in sources.split(',')]

    cmd = 'tar -{0} {1} {2}'.format(options, tarfile, ' '.join(sources))
    return __salt__['cmd.run'](cmd, cwd=cwd, template=template).splitlines()


@decorators.which('gzip')
def gzip(sourcefile, template=None):
    '''
    Uses the gzip command to create gzip files

    CLI Example to create ``/tmp/sourcefile.txt.gz``::

        salt '*' archive.gzip /tmp/sourcefile.txt

    The template arg can be set to 'jinja' or another supported template
    engine to render the command arguments before execution.
    CLI Example::

        salt '*' archive.gzip template=jinja /tmp/{{grains.id}}.txt

    '''
    cmd = 'gzip {0}'.format(sourcefile)
    return __salt__['cmd.run'](cmd, template=template).splitlines()


@decorators.which('gunzip')
def gunzip(gzipfile, template=None):
    '''
    Uses the gunzip command to unpack gzip files

    CLI Example to create ``/tmp/sourcefile.txt``::

        salt '*' archive.gunzip /tmp/sourcefile.txt.gz

    The template arg can be set to 'jinja' or another supported template
    engine to render the command arguments before execution.
    CLI Example::

        salt '*' archive.gunzip template=jinja /tmp/{{grains.id}}.txt.gz

    '''
    cmd = 'gunzip {0}'.format(gzipfile)
    return __salt__['cmd.run'](cmd, template=template).splitlines()


@decorators.which('zip')
def zip_(zipfile, sources, template=None):
    '''
    Uses the zip command to create zip files

    CLI Example::

        salt '*' archive.zip /tmp/zipfile.zip /tmp/sourcefile1,/tmp/sourcefile2

    The template arg can be set to 'jinja' or another supported template
    engine to render the command arguments before execution.
    For example::

        salt '*' archive.zip template=jinja /tmp/zipfile.zip \
                /tmp/sourcefile1,/tmp/{{grains.id}}.txt

    '''
    if isinstance(sources, salt._compat.string_types):
        sources = [s.strip() for s in sources.split(',')]
    cmd = 'zip {0} {1}'.format(zipfile, ' '.join(sources))
    return __salt__['cmd.run'](cmd, template=template).splitlines()


@decorators.which('unzip')
def unzip(zipfile, dest, template=None, *xfiles):
    '''
    Uses the unzip command to unpack zip files

    CLI Example::

        salt '*' archive.unzip /tmp/zipfile.zip /home/strongbad/ file_1 file_2

    The template arg can be set to 'jinja' or another supported template
    engine to render the command arguments before execution.
    For example::

        salt '*' archive.unzip template=jinja /tmp/zipfile.zip /tmp/{{grains.id}}/ file_1 file_2

    '''
    xfileslist = ' '.join(xfiles)
    cmd = 'unzip {0} -d {1}'.format(zipfile, dest)
    if xfileslist:
        cmd = cmd + ' -x {0}'.format(xfiles)
    out = __salt__['cmd.run'](cmd, template=template).splitlines()
    return out


@decorators.which('rar')
def rar(rarfile, template=None, *sources):
    '''
    Uses the rar command to create rar files
    Uses rar for Linux from http://www.rarlab.com/

    CLI Example::

        salt '*' archive.rar /tmp/rarfile.rar /tmp/sourcefile1 /tmp/sourcefile2

    The template arg can be set to 'jinja' or another supported template
    engine to render the command arguments before execution.
    For example::

        salt '*' archive.rar template=jinja /tmp/rarfile.rar /tmp/sourcefile1 /tmp/{{grains.id}}.txt


    '''
    # TODO: Check that len(sources) >= 1
    sourcefiles = ' '.join(sources)
    cmd = 'rar a -idp {0} {1}'.format(rarfile, sourcefiles)
    out = __salt__['cmd.run'](cmd, template=template).splitlines()
    return out


@decorators.which('unrar')
def unrar(rarfile, dest, template=None, *xfiles):
    '''
    Uses the unrar command to unpack rar files
    Uses rar for Linux from http://www.rarlab.com/

    CLI Example::

        salt '*' archive.unrar /tmp/rarfile.rar /home/strongbad/ file_1 file_2

    The template arg can be set to 'jinja' or another supported template
    engine to render the command arguments before execution.
    For example::

        salt '*' archive.unrar template=jinja /tmp/rarfile.rar /tmp/{{grains.id}}/ file_1 file_2

    '''
    xfileslist = ' '.join(xfiles)
    cmd = 'rar x -idp {0}'.format(rarfile, dest)
    if xfileslist:
        cmd = cmd + ' {0}'.format(xfiles)
    cmd = cmd + ' {0}'.format(dest)
    out = __salt__['cmd.run'](cmd, template=template).splitlines()
    return out
