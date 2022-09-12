import os
import sys
import subprocess
from pathlib import Path
from logging import getLogger, basicConfig, INFO
from argparse import ArgumentParser

if sys.version_info >= (3, 11):
    import tomllib  # pylint: disable=import-error
else:
    import tomli as tomllib

logger = getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent.resolve()
PKGS_SRC_DIR = ROOT_DIR / 'pkgs'
PKGS_BILD_DIR = ROOT_DIR / 'build/repo'


def parse_args():
    parser = ArgumentParser(prog="axju-os-build")
    parser.add_argument('pkgs', nargs="*")

    return parser, parser.parse_args()


def iter_pkgs(pkgs_dir: Path = PKGS_SRC_DIR):
    """return list with all pkg urls"""
    for path in pkgs_dir.iterdir():
        yield path


def load_conf(path: Path = Path('conf.toml').resolve()):
    with path.open("rb") as file:
        return tomllib.load(file)


def call_cmd(args, env: dict = {}):
    _env = dict(os.environ)
    _env.update(env)
    process = subprocess.Popen(args, env=_env)
    exitcode = process.wait()


def make_pkgs(build_dir: Path = PKGS_BILD_DIR, pkgs: list = []):
    logger.info("build all pkgs")
    build_dir.mkdir(parents=True, exist_ok=True)
    for pkg in iter_pkgs():
        if pkgs and pkg.name not in pkgs:
            continue
        logger.info("build pkg: %s", pkg.name)
        os.chdir(pkg)
        call_cmd(["makepkg", "-Ccf"], env={"PKGDEST": str(build_dir)})


def make_repo(repo_dir: Path = PKGS_BILD_DIR):
    logger.info("create/update repo")
    os.chdir(repo_dir)
    for path in repo_dir.glob('*.pkg.tar.zst'):
        logger.info("add: %s", path)
        call_cmd(['repo-add', 'axju.db.tar.gz', path])


def upload_repo(scp_path: str, path: Path = PKGS_BILD_DIR):
    logger.info("upload repo")
    for file in path.iterdir():
        call_cmd([
            'scp', file, scp_path
        ])


def main():
    _, args = parse_args()
    basicConfig(level=INFO, format="%(asctime)s %(message)s")

    call_cmd(['git', 'submodule', 'update', '--remote', '--recursive'])
    arch = subprocess.check_output(['uname', '-m']).decode().strip('\n')
    logger.info('build pkgs for %s', arch)

    # make_pkgs(pkgs=args.pkgs)
    make_repo()

    conf = load_conf()
    if conf_u := conf.get('upload'):
        if conf_scp_path := conf_u.get('scp_path'):
            scp_path = conf_scp_path.format(arch=arch)
            upload_repo(scp_path)


if __name__ == '__main__':
    main()

