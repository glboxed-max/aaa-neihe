#!/usr/bin/env python3
# ===== 说明：校验 shell 脚本语法（bash -n） =====
# 来源：WildKernels/GKI_KernelSU_SUSFS 的 .github/scripts/validate_shell.py
import concurrent.futures
import pathlib
import subprocess
import sys

EXCLUDE_DIRS = {".git"}


def find_shell_files(root="."):
    for path in pathlib.Path(root).rglob("*.sh"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        yield path


def check_file(path):
    result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
    if result.returncode != 0:
        return path, result.stderr.strip()
    return path, None


def main():
    files = sorted(find_shell_files())
    if not files:
        print("未找到 shell 脚本。")
        return 0
    status = 0
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for path, error in executor.map(check_file, files):
            if error:
                print(f"语法错误：{path}")
                print(f"  {error}")
                status = 1
    print(f"已检查 {len(files)} 个 shell 脚本。")
    return status


if __name__ == "__main__":
    sys.exit(main())
