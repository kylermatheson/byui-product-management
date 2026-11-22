#!/usr/bin/env python3
"""Build the downloadable starter deterministically from the local source files."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'course-support' / 'starter'
TARGET = ROOT / 'course-support' / 'byui-product-management-starter.zip'


def build():
    with ZipFile(TARGET, 'w', compression=ZIP_DEFLATED) as archive:
        for path in sorted(SOURCE.rglob('*')):
            if not path.is_file():
                continue
            name = 'byui-product-management-starter/' + path.relative_to(SOURCE).as_posix()
            info = ZipInfo(name, date_time=(2027, 2, 22, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    print(f'Built {TARGET.relative_to(ROOT)}')


if __name__ == '__main__':
    build()
