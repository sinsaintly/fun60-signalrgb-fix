"""Patch the tested MonsGeek v4 bundle; dry-run unless --apply is supplied."""
import argparse
import datetime
import os
from pathlib import Path
import re
import shutil
import subprocess


def transform(source):
    if '__fun60Share' in source:
        raise ValueError('Legacy UDP sharing patch detected. Restore its pre-sharing backup first.')
    for v in ('i', 't'):
        original = f'new DataView({v}.buffer,{v}.byteOffset,{v}.byteLength).getUint32(1,!0)'
        fixed = (f'({v}[1]===77&&{v}[2]===9&&{v}[3]===70&&{v}[4]===54&&'
                 f'{v}[5]===80&&{v}[6]===75?2381:{original})')
        if source.count(fixed) == 1:
            continue
        # Only touch the identity reader with the exact tested surrounding expression.
        if source.count(original) != 1:
            raise ValueError(f'Unsupported bundle: expected one {v} identity reader.')
        source = source.replace(original, fixed, 1)
    start = source.find('whoAmI=async()=>{for(let t=0;t<')
    if start == -1:
        raise ValueError('Unsupported bundle: identity retry function missing.')
    end = source.find(';destory=', start)
    if end == -1:
        raise ValueError('Unsupported bundle: identity retry boundary missing.')
    section = source[start:end]
    fast = 't<(this.deviceType.vid===12625&&this.deviceType.pid===20525?15:3)'
    if fast not in section:
        if not section.startswith('whoAmI=async()=>{for(let t=0;t<3;t++){for(;!this.isOnline;)') or section.count('await Je(500)') != 1:
            raise ValueError('Unsupported bundle: retry function differs from tested version.')
        section = section.replace('t<3', fast, 1).replace(
            'await Je(500)', 'await Je(this.deviceType.vid===12625&&this.deviceType.pid===20525?100:500)')
    return source[:start] + section + source[end:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default = Path(os.environ.get('LOCALAPPDATA', '.')) / 'Programs/MonsGeek Driver v4/resources/app/dist/js/index.f9e8588e.js'
    parser.add_argument('--bundle', type=Path, default=default)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    original = args.bundle.read_bytes()
    updated = transform(original.decode('utf-8-sig')).encode('utf-8')
    if updated == original:
        print('Already patched. No changes needed.')
        return
    if not args.apply:
        print('Compatible bundle. Dry run passed; no files changed. Add --apply to install.')
        return
    if os.name == 'nt':
        processes = subprocess.run(['tasklist', '/FO', 'CSV', '/NH'], capture_output=True, text=True, check=True).stdout
        if 'monsgeek driver v4.exe' in processes.lower():
            raise ValueError('Fully exit MonsGeek, including its tray icon, before applying.')
    backup = args.bundle.with_name(args.bundle.name + '.fun60-backup-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    shutil.copy2(args.bundle, backup)
    temporary = args.bundle.with_name(args.bundle.name + '.fun60-tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    os.replace(temporary, args.bundle)
    print(f'Patch installed. Backup: {backup}\nReopen MonsGeek to verify FUN60 Ultra detection.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        raise SystemExit(str(error))
