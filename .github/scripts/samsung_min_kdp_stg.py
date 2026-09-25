#!/usr/bin/env python3
# ===== 说明：三星 min_kdp 的 .stg 幂等插入回退脚本 =====
# 来源：WildKernels/GKI_KernelSU_SUSFS 的 actions/apply-device-patches 内嵌 python
# 用途：当刚性补丁因上游漂移失败时，把 kdp_* 的 ABI 函数/符号/接口 id 幂等插入 .stg 文件。
# 用法：python3 samsung_min_kdp_stg.py <abi_gki_aarch64.stg>
import sys


def main():
    if len(sys.argv) != 2:
        print("用法: samsung_min_kdp_stg.py <abi_gki_aarch64.stg>", file=sys.stderr)
        return 2
    path = sys.argv[1]
    with open(path) as f:
        src = f.read()

    def ensure_before(anchor, block, label):
        nonlocal src
        if label in src:
            print("已存在:", label)
            return
        if anchor in src:
            src = src.replace(anchor, block + anchor, 1)
            print("已插入", label)
        else:
            if not src.endswith("\n"):
                src += "\n"
            src += block
            print("已插入", label, "(EOF)")

    func1 = ('function {\n  id: 0x1e5195df\n  return_type_id: 0x48b5725f\n'
             '  parameter_id: 0x3d551c03\n  parameter_id: 0x6720d32f\n}\n')
    func2 = ('function {\n  id: 0xc18e39fb\n  return_type_id: 0x4585663f\n'
             '  parameter_id: 0x3d551c03\n}\n')
    elf1 = ('elf_symbol {\n  id: 0xb0801f6e\n  name: "kdp_set_cred_non_rcu"\n  is_defined: true\n'
            '  symbol_type: FUNCTION\n  crc: 0x738bae5e\n  type_id: 0x1e5195df\n'
            '  full_name: "kdp_set_cred_non_rcu"\n}\n')
    elf2 = ('elf_symbol {\n  id: 0x3037c5bc\n  name: "kdp_usecount_dec_and_test"\n  is_defined: true\n'
            '  symbol_type: FUNCTION\n  crc: 0xda582aa5\n  type_id: 0xc18e39fb\n'
            '  full_name: "kdp_usecount_dec_and_test"\n}\n')
    elf3 = ('elf_symbol {\n  id: 0x8334a496\n  name: "kdp_usecount_inc"\n  is_defined: true\n'
            '  symbol_type: FUNCTION\n  crc: 0xfb342499\n  type_id: 0x1fcd1693\n'
            '  full_name: "kdp_usecount_inc"\n}\n')

    ensure_before('function {\n  id: 0x1e571002', func1, 'id: 0x1e5195df')
    ensure_before('function {\n  id: 0xc18f1240', func2, 'id: 0xc18e39fb')
    anchor = 'elf_symbol {\n  id: 0x493ce9fc\n  name: "loops_per_jiffy"'
    for block, label in [(elf1, '"kdp_set_cred_non_rcu"'),
                         (elf2, '"kdp_usecount_dec_and_test"'),
                         (elf3, '"kdp_usecount_inc"')]:
        ensure_before(anchor, block, label)

    ids = ['0xb0801f6e', '0x3037c5bc', '0x8334a496']
    missing = [i for i in ids if f'symbol_id: {i}' not in src]
    if missing:
        lines = [f'  symbol_id: {i}\n' for i in missing]
        a = '  symbol_id: 0xc750a072\n'
        if a in src:
            src = src.replace(a, a + ''.join(lines), 1)
            print("已插入 interface ids:", missing)
        else:
            idx = src.find('interface {')
            assert idx != -1, "未找到 interface 块"
            end = src.find('\n}\n', idx)
            assert end != -1, "未找到 interface 结束"
            src = src[:end] + ''.join(lines).rstrip('\n') + src[end:]
            print("已插入 interface ids（interface 结束前）:", missing)
    else:
        print("interface ids 已存在")

    with open(path, 'w') as f:
        f.write(src)
    print("回退 .stg 插入完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
