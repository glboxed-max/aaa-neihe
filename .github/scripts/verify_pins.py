#!/usr/bin/env python3
# ===== 说明：校验/更新依赖 pins（版本锁定） =====
# 来源：WildKernels/GKI_KernelSU_SUSFS 的 .github/scripts/update_verified_pins.py（简化版）
#
# 作用：
#   1) 校验 .github/pins/verified.json 里每个 sha 在对应仓库中真实存在；
#   2) 对比记录 sha 与分支最新 sha，报告是否漂移；
#   3) 传 --update 时，把记录更新为分支最新 sha（用于手动提升/定期刷新）。
#
# 用法：python3 .github/scripts/verify_pins.py [--update]
import json
import os
import subprocess
import sys
import urllib.request

PINS = ".github/pins/verified.json"


def gh_get(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "aaa-neihe-pins",
    })
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status


def ls_remote(repo, ref):
    out = subprocess.run(
        ["git", "ls-remote", f"https://github.com/{repo}.git", f"refs/heads/{ref}"],
        capture_output=True, text=True,
    ).stdout.strip()
    return out.split("\t")[0] if out else ""


def main():
    update = "--update" in sys.argv
    with open(PINS, encoding="utf-8") as f:
        data = json.load(f)

    changed = False
    drift = []
    missing = []
    print(f"{'名称':<16} {'仓库':<34} {'分支':<10} 状态")
    for name, pin in data["pins"].items():
        repo, ref, sha = pin["repo"], pin["ref"], pin["sha"]

        # 1) sha 是否存在
        try:
            status = gh_get(f"https://api.github.com/repos/{repo}/commits/{sha}")
            exists = status == 200
        except Exception:
            exists = None
        if exists is False:
            missing.append(name)

        # 2) 分支最新 sha
        latest = ls_remote(repo, ref)
        state = []
        if exists is False:
            state.append("sha 不存在")
        if latest and latest != sha:
            state.append(f"分支已更新 -> {latest[:12]}")
            drift.append((name, latest))
        elif latest:
            state.append("最新")

        print(f"{name:<16} {repo:<34} {ref:<10} " + ("; ".join(state) if state else "未知/离线"))
        if update and latest and latest != sha:
            pin["sha"] = latest
            changed = True

    if update and changed:
        data["generated_at"] = subprocess.run(
            ["date", "-u", "+%Y-%m-%d"], capture_output=True, text=True
        ).stdout.strip()
        with open(PINS, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("\n已更新 pins 文件。")

    if missing:
        print("\n::error::以下 pin 的 sha 不存在：" + ", ".join(missing))
        return 1
    if drift:
        print("\n提示：存在分支漂移（不影响构建，构建按记录的 sha 锁定）：")
        for name, latest in drift:
            print(f"  - {name}: {latest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
