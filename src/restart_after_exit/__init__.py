import os
import sys
from pathlib import Path
import other_package

current_version = 'v0.1.0'


def need_update(current_version):
    version_file = Path(__file__).with_name('latest_version.txt')
    with open(version_file, 'r') as f:
        latest_version = f.read().strip()
        if latest_version > current_version:
            print('need update, from {} to {}'.format(current_version, latest_version))
            return True
        else:
            return False


def restart_after_exit():
    python = sys.executable
    os.execl(python, python, *sys.argv)


def download_update_files_to_cache_path():
    return []


def check_md5(update_files):
    return True


def do_real_update():
    pass


def launch_main_app():
    pass


def mock_latest_version():
    version_file = Path(__file__).with_name('latest_version.txt')
    with open(version_file, 'w') as f:
        f.write(str(current_version))


def main():
    if need_update(current_version):
        update_files = download_update_files_to_cache_path()
        if check_md5(update_files):
            do_real_update()
            mock_latest_version()
            restart_after_exit()
        else:
            print('download update files corrupted')
    print('this version is latest, no need to update')

    launch_main_app()


if __name__ == '__main__':
    main()
