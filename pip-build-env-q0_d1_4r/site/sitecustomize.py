
import os, site, sys

# First, drop system-sites related paths.
original_sys_path = sys.path[:]
known_paths = set()
for path in {'d:\\desktop\\眼科公共数据库agent搭建\\.venv\\lib\\site-packages'}:
    site.addsitedir(path, known_paths=known_paths)
system_paths = set(
    os.path.normcase(path)
    for path in sys.path[len(original_sys_path):]
)
original_sys_path = [
    path for path in original_sys_path
    if os.path.normcase(path) not in system_paths
]
sys.path = original_sys_path

# Second, add lib directories.
# ensuring .pth file are processed.
for path in ['D:\\Desktop\\眼科公共数据库agent搭建\\pip-build-env-q0_d1_4r\\overlay\\Lib\\site-packages', 'D:\\Desktop\\眼科公共数据库agent搭建\\pip-build-env-q0_d1_4r\\normal\\Lib\\site-packages']:
    assert not path in sys.path
    site.addsitedir(path)
