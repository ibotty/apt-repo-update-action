import os
import git
import gnupg
import json
import logging
import pathlib
import re
import shutil

from debian.debfile import DebFile

debug = os.environ.get('INPUT_DEBUG', False)

if debug:
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

if __name__ == '__main__':
    logging.info('-- Parsing input --')

    github_token = os.environ.get('INPUT_GITHUB_TOKEN')
    supported_arch = os.environ.get('INPUT_REPO_SUPPORTED_ARCH')
    supported_distro = os.environ.get('INPUT_REPO_SUPPORTED_DISTRO')

    github_repo = os.environ.get('GITHUB_REPOSITORY')

    apt_folder = os.environ.get('INPUT_REPO_DIRECTORY', 'apt')
    update_folder = os.environ.get('INPUT_UPDATE_DIRECTORY', 'updates')

    if None in (github_token, supported_arch, supported_distro):
        logging.error('Required key is missing')
        sys.exit(1)

    supported_arch_list = supported_arch.strip().split('\n')
    supported_distro_list = supported_distro.strip().split('\n')

    logging.debug(github_token)
    logging.debug(supported_arch_list)
    logging.debug(supported_distro_list)

    key_private = os.environ.get('INPUT_PRIVATE_KEY')
    key_passphrase = os.environ.get('INPUT_KEY_PASSPHRASE')

    logging.debug(key_private)
    logging.debug(key_passphrase)

#    logging.info('-- Done parsing input --')

    # Clone repo

    logging.info('-- Cloning current Github page --')

    github_user = github_repo.split('/')[0]
    github_slug = github_repo.split('/')[1]

    if os.path.exists(github_slug):
        shutil.rmtree(github_slug)

    git_repo = git.Repo.clone_from(
        'https://{}@github.com/{}.git'.format(github_token, github_repo),
        github_slug,
    )

    git_refs = git_repo.remotes.origin.refs
    git_refs_name = list(map(lambda x: str(x).split('/')[-1], git_refs))

    logging.debug(git_refs_name)

    logging.info('-- Done cloning current Github page --')

    # Set directories
    update_dir = github_slug + '/' + update_folder
    apt_dir = github_slug + '/' + apt_folder

    os.chdir(apt_dir)

    # Prepare key

    logging.info('-- Importing and preparing GPG key --')

    gpg = gnupg.GPG()
    private_import_result = gpg.import_keys(private_key)

    if private_import_result.count != 1
      logging.error('Invalid private key provided; please provide 1 valid key.')
      sys.exit(1)

    logging.debug(private_import_result)

    if not any(data['ok'] >= '16' for data in private_import_result.results):
        logging.error('Key provided is not a secret key')
        sys.exit(1)

    private_key_id = private_import_result.results[0]['fingerprint']

    logging.info('Using key:', private_key_id)

    # Signing to unlock key on gpg agent
    gpg.sign('test', keyid=private_key_id, passphrase=key_passphrase)

    logging.info('-- Done importing key --')

    # Process files.

    logging.info('-- Processing updates --')

    # Enumerate files.
    files = [f for f in os.listdir(update_dir) if os.path.isfile(f) and pathlib.Path(f).suffix == ".deb"]
    for file in files:

        logging.info('Currently processing: ', file)
