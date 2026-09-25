#!/usr/bin/env python3
# ===== 说明：校验 python 脚本语法（ast.parse） =====
# 来源：WildKernels/GKI_KernelSU_SUSFS 的 .github/scripts/validate_python.py
import ast
import concurrent.futures
import pathlib
import sys

EXCLUDE_DIRS = {".git", "venv", ".venv"}


def find_python_files(root="."):
    for path in pathlib.Path(root).rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        yield path


def check_file(path):
    try:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
        return path, None
    except SyntaxError as error:
        return path, f"行 {error.lineno}, 列 {error.offset}: {error.msg}"
    except UnicodeDecodeError as error:
        return path, f"编码错误：{error}"


def main():
    files = sorted(find_python_files())
    if not files:
        print("未找到 python 文件。")
        return 0
    status = 0
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for path, error in executor.map(check_file, files):
            if error:
                print(f"语法错误：{path}")
                print(f"  {error}")
                status = 1
    print(f"已检查 {len(files)} 个 python 文件。")
    return status


if __name__ == "__main__":
    sys.exit(main())
