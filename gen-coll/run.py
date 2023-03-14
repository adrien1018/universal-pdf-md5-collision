#!/usr/bin/env python3

import subprocess, os, shutil, sys, time, tempfile, argparse
import os.path

hashclash_dir = './hashclash'

def FindColl(file, logfile, x, orig_size):
    cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tempdir, open(logfile, 'ab') as logf:
            shutil.copyfile(file, os.path.join(tempdir, 'in'))
            os.chdir(tempdir)
            logf.write(f'[{time.time():.3f}] Start\n'.encode())
            logf.flush()
            subprocess.run([os.path.join(hashclash_dir, 'scripts/poc_no_mod.sh'), 'in'], stdout=logf, stderr=logf)
            logf.write(f'[{time.time():.3f}] End\n'.encode())
            logf.flush()
            if not os.path.exists('collision1.bin'):
                return None, None
            with open('collision1.bin', 'rb') as f1, open('collision2.bin', 'rb') as f2:
                data1 = f1.read()[orig_size:]
                data2 = f2.read()[orig_size:]
            return data1, data2
    finally:
        os.chdir(cwd)

def Work(x):
    orig_size = os.stat('collisions-1').st_size
    flag = True
    while flag:
        print(f'[{time.time():.3f}] Start collision {x}', flush=True)
        shutil.copyfile('collisions-1', 'collisions.tmp')
        with open('collisions.tmp', 'ab') as f:
            f.write(f'     \n{x:4d} 0 R %'.encode())
        data1, data2 = FindColl('collisions.tmp', f'logs/{x:04d}', x, orig_size)
        print(f'[{time.time():.3f}] Collision pair {x}: {data1} {data2}', flush=True)
        if data1 and not any((c in b'\0\r\n') for c in data1[7:] + data2[7:]):
            with open('collisions-1', 'ab') as f1, open('collisions-2', 'ab') as f2:
                f1.write(data1)
                f2.write(data2)
            flag = False
        print(f'[{time.time():.3f}] Collision {x}, success:', not flag, flush=True)

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--hashclash-dir',
                    help="Directory of hashclash (must be already compiled)")
parser.add_argument('start', nargs='?', type=int, default=1000,
                    help="Starting object ID")
parser.add_argument('end', nargs='?', type=int, default=7900,
                    help="Ending object ID")
args = parser.parse_args()
if args.hashclash_dir:
    hashclash_dir = args.hashclash_dir
hashclash_dir = os.path.abspath(hashclash_dir)

shutil.copy('poc_no_mod.sh', os.path.join(hashclash_dir, 'scripts/'))
os.makedirs('logs', exist_ok=True)

if not os.path.exists('collisions-1'):
    shutil.copyfile('table-prefix', 'collisions-1')
    shutil.copyfile('table-prefix', 'collisions-2')

for i in range(args.start, args.end, 2):
    Work(i)
