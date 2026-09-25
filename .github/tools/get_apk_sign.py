#!/usr/bin/env python3
"""计算 KernelSU 管理器签名 (size, hash)。

复刻 KernelSU 的算法：
  kernel/manager/apk_sign.c 的 check_v2_signature()
  userspace/ksud/src/apk_sign.rs 的 get_apk_signature()
即：从 APK Signing Block 的 v2 块里取出「签名证书」，
    size = 证书字节长度，hash = 证书字节的 SHA-256（小写 hex）。

输出（便于 shell 解析）：
  SIZE=0x...
  HASH=<sha256hex>

用法: python3 get_apk_sign.py <apk>
"""
import hashlib
import struct
import sys

EOCD_MAGIC = 0x06054B50
SIG_BLOCK_MAGIC = b"APK Sig Block 42"
V2_ID = 0x7109871A


def u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def u64(b, o):
    return struct.unpack_from("<Q", b, o)[0]


def get_sign(path):
    with open(path, "rb") as f:
        data = f.read()
    n = len(data)

    # 1) 从尾部找 EOCD
    eocd = -1
    for i in range(0, 0xFFFF + 1):
        pos = n - i - 2
        if pos < 0:
            break
        if u16(data, pos) == i:
            magic_pos = pos - 20
            if magic_pos >= 0 and u32(data, magic_pos) == EOCD_MAGIC:
                eocd = magic_pos
                break
    if eocd < 0:
        raise SystemExit("EOCD not found (not a zip/apk?)")

    cd_size = u32(data, eocd + 12)
    cd_offset = u32(data, eocd + 16)
    if cd_offset < 0x20:
        raise SystemExit("bad central directory offset")

    # 2) 定位 APK Signing Block（在中央目录之前）
    pairs_end = cd_offset - 0x18
    size8 = u64(data, pairs_end)  # 尾部 size 字段
    if data[pairs_end + 8:pairs_end + 8 + 16] != SIG_BLOCK_MAGIC:
        raise SystemExit("no APK Sig Block (unsigned APK?)")

    start = cd_offset - size8 - 8
    if start < 0:
        raise SystemExit("bad signing block size")
    size_of_block = u64(data, start)
    if size_of_block != size8:
        raise SystemExit("signing block size mismatch")

    # 3) 遍历 pair，找 v2 (0x7109871a)
    p = start + 8
    end = pairs_end
    v2 = None
    while p < end:
        length = u64(data, p)
        p += 8
        if length == size_of_block:
            break
        pid = u32(data, p)
        p += 4
        value = data[p:p + (length - 4)]
        p += length - 4
        if pid == V2_ID:
            v2 = value

    if v2 is None:
        raise SystemExit("no v2 signature block found")

    # 4) 解析 v2: 顺序 -> 首个 signer -> signed data -> (跳过 digests) -> certificates -> 首个证书
    b = v2
    o = 0
    o += 4  # signers sequence length
    o += 4  # signer length
    o += 4  # signed data length
    digests_len = u32(b, o)
    o += 4 + digests_len
    o += 4  # certificates sequence length
    cert_len = u32(b, o)
    o += 4
    cert = b[o:o + cert_len]

    if len(cert) != cert_len:
        raise SystemExit("certificate truncated")
    return cert_len, hashlib.sha256(cert).hexdigest()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: get_apk_sign.py <apk>")
    size, digest = get_sign(sys.argv[1])
    print(f"SIZE=0x{size:x}")
    print(f"HASH={digest}")
