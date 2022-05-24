import fire
import os
import shutil
from loguru import logger
from pathlib import Path
from plumbum import local
from typing import Iterator


# # Helpers

# +
def switch_folder(source_folder:str, destination_folder:str,
                  filepath:str, create_destination_dirs:bool=False) -> str:
    """
    Switches the folder where a file is located.

    It will reproduce the folder structure of `source_folder` in `destination_folder`
    in the output string.

    Optionally it can also create corresponding folders in `destination_folder` (when
    `create_destination_dirs=True`).

    Examples
    --------
    >>> FileOperations.switch_folder('D:/', 'C:/Test', filepath='D:/foo.md', create_missing_dirs=False)
    'C:/Test/foo.md'

    >>> FileOperations.switch_folder('D:/', 'C:/Test', filepath='D:/Subfolder/foo.md', create_missing_dirs=False)
    'C:/Test/Subfolder/foo.md'

    >>> FileOperations.switch_folder('/home/my_lib/docs', '/home/test', filepath='/home/my_lib/docs/foo.md',
    ...                              create_missing_dirs=False)
    '/home/test/foo.md'

    >>> FileOperations.switch_folder('/home/my_lib/docs', '/home/test', filepath='/home/my_lib/docs/subfolder/foo.md',
    ...                              create_missing_dirs=False)
    '/home/test/subfolder/foo.md'
    """
    relpath = os.path.relpath(filepath, source_folder)
    destination_path = os.path.join(destination_folder, relpath)
    if create_destination_dirs:
        destination_folder = Path(destination_path).parent
        destination_folder.mkdir(parents=True, exist_ok=True)
    return destination_path


class Exclusions:
    """
    Folders, file extensions, filenames, ... to exclude from the public release of my
    resume.
    """
    folders = ('.git', '.ipynb_checkpoints', '.vs', '.virtual_documents')
    exts = ('insyncdl',)
    filenames = tuple()  # I needed that before, I'll just leave it here

    def matches(filepath:str, /):
        """
        Checks if given filepath is to be excluded from the public release

        Examples
        --------
        >>> Exclusions.matches('/foo/.git/objects')
        True
        >>> Exclusions.matches('/foo/.ipynb_checkpoints/a.ipynb')
        True
        >>> Exclusions.matches('/foo/.vs')
        True
        """
        return (any(c in Path(filepath).parts for c in Exclusions.folders) or
                any(Path(filepath).name.endswith(c) for c in Exclusions.exts) or
                Path(filepath).name in Exclusions.filenames)


def rlistdir(folder:str, /) -> Iterator[str]:
    """
    Recursive directory listing (files only and with full filepath)
    """
    for path, subdirs, files in os.walk(folder):
        for name in files:
            yield str(Path(os.path.join(path, name)).resolve())


def git_push_no_history(git_folder:str, default_branch:str, commit_msg:str='autocommit') -> None:
    """
    Stages all files in a git folder, commits them using message `commit_msg` and pushes
    changes overwriting any previous commit (the public release of my resume will always
    have one commit for privacy reasons).
    """
    # get git command
    git = local['git']

    # see https://stackoverflow.com/a/13102849
    with local.cwd(git_folder):
        git['checkout', '--orphan', 'newBranch']()
        git['add', '-A']()  # Add all files and commit them
        git['commit', '-m', 'autocommit', '--allow-empty']()
        git['branch', '-D', default_branch]()  # Deletes the default branch
        git['branch', '-m', default_branch]()  # Rename the current branch to default branch
        git['push', '-f', 'origin', default_branch]()  # Force push default branch to github
        git['gc', '--aggressive', '--prune=all']()     # remove the old files


# -

# # Main function

def main(source:str= '.', destination:str= '../resume_public', default_branch:str='main') -> None:
    """
    Makes a public release of my resume at https://github.com/ThibTrip/resume_public

    Warnings
    --------
    The git history is not kept for the public release. There is always only one commit.

    Parameters
    ----------
    source
        Location of the private repository `resume` on disk
    destination
        Location of the public repository `resume_public` on disk
    default_branch
        Default branch of the `resume_public` repo
    """

    # make sure we don't overwrite our folder!
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    assert source != destination, 'source == destination!'

    # find files to copy
    to_copy = [fp for fp in rlistdir(source) if not Exclusions.matches(fp)]

    # find paths to delete
    # 1) find all existing paths in destination folder
    # 2) switch folder of paths in `to_copy`
    # 3) compare 1 and 2 to determine what needs to be deleted
    paths_destination = [fp for fp in rlistdir(destination) if not Exclusions.matches(fp)]
    new_paths = [switch_folder(source_folder=source, destination_folder=destination, filepath=fp)
                 for fp in to_copy]
    to_delete = [p for p in paths_destination if p not in new_paths]

    # delete files
    for filepath in to_delete:
        logger.info(f'Removing "{filepath}"')
        os.remove(filepath)

    # copy files
    for filepath in to_copy:
        new_path = switch_folder(source_folder=source, destination_folder=destination, filepath=filepath,
                                 create_destination_dirs=True)
        logger.info(f'Adding/replacing "{new_path}"')
        shutil.copy2(src=filepath, dst=new_path)

    # git push
    logger.info('Pushing to GitHub')
    git_push_no_history(git_folder=destination, default_branch=default_branch)
    logger.info('Done!')


# # Run main function in CLI

if __name__ == '__main__':
    fire.Fire(main)
