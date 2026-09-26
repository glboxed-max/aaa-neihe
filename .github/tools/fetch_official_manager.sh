#!/usr/bin/env bash
# ===== 说明：按【严格对应版本】获取上游官方管理器 APK =====
# 规则（AGENTS.md 第 3/6 条）：管理器必须与所选 KernelSU 提交对应，禁止跨版本混用。
# 因此这里只取“与目标 commit 相同的上游 CI 产物”（Actions artifacts），
# 而不是“最新 Release”。取不到就直接失败，绝不拿其它版本顶替。
#
# 用法: fetch_official_manager.sh <variant> <ref-or-sha|空> <输出APK路径> [解包目录]
#   variant: SukiSU | ReSukiSU | Official | Next
#   ref-or-sha: 分支/Tag/commit；留空用该仓库默认分支
# 产物：<输出APK路径>（官方同版本 APK）；若给出解包目录，还会把 libksud.so 解到 <解包目录>/libksud/<abi>/
set -euo pipefail

variant="${1:?variant}"
ref="${2:-}"
out_apk="${3:?out_apk}"
extract_dir="${4:-}"

case "$variant" in
  SukiSU)   repo="SukiSU-Ultra/SukiSU-Ultra";       wf="build-manager.yml";    dref="main" ;;
  ReSukiSU) repo="ReSukiSU/ReSukiSU";               wf="build-manager.yml";    dref="main" ;;
  Official) repo="tiann/KernelSU";                  wf="build-manager.yml";    dref="main" ;;
  Next)     repo="KernelSU-Next/KernelSU-Next";     wf="build-manager-ci.yml"; dref="dev"  ;;
  *) echo "::error::未知变体 $variant"; exit 1 ;;
esac

# 解析 commit（40 位 sha 直接用；否则 ls-remote 解析分支/tag）
if [[ "$ref" =~ ^[0-9a-f]{40}$ ]]; then
  sha="$ref"
else
  [ -n "$ref" ] || ref="$dref"
  sha="$(git ls-remote "https://github.com/$repo.git" "$ref" 2>/dev/null | awk '{print $1; exit}')"
  # 允许直接传 tag 名
  if [ -z "$sha" ]; then
    sha="$(git ls-remote "https://github.com/$repo.git" "refs/tags/$ref" 2>/dev/null | awk '{print $1; exit}')"
  fi
fi
[ -n "$sha" ] || { echo "::error::无法解析 $repo 的 ref '$ref'"; exit 1; }
echo "目标管理器：$repo @ $sha（workflow $wf）"

# 找该 commit 的上游 CI 运行
run_id="$(gh api "repos/$repo/actions/workflows/$wf/runs?head_sha=$sha&per_page=1" \
  --jq '.workflow_runs[0].id // empty' 2>/dev/null || true)"
if [ -z "$run_id" ]; then
  echo "::error::$repo 在 commit $sha 上没有 $wf 的构建产物。"
  echo "::error::按规则不使用其它版本的管理器；请改选有产物的 commit，或先用 manager-build 从源码构建。"
  exit 1
fi
echo "使用上游运行: $run_id"

# 列出未过期产物
art_ids="$(gh api "repos/$repo/actions/runs/$run_id/artifacts?per_page=100" \
  --jq '.artifacts[] | select(.expired==false) | .id' 2>/dev/null || true)"
[ -n "$art_ids" ] || { echo "::error::运行 $run_id 没有可用产物"; exit 1; }

tmp="$(mktemp -d)"
found=""
while IFS= read -r aid; do
  [ -n "$aid" ] || continue
  gh api "repos/$repo/actions/artifacts/$aid/zip" > "$tmp/$aid.zip" 2>/dev/null || continue
  unzip -o -q "$tmp/$aid.zip" -d "$tmp/$aid" 2>/dev/null || true
  apk="$(find "$tmp/$aid" -type f -name '*.apk' | head -n1 || true)"
  if [ -n "$apk" ]; then
    # 优先取带 libksud.so 的（完整管理器）
    if unzip -l "$apk" 2>/dev/null | grep -q 'lib/.*/libksud.so'; then
      found="$apk"; break
    fi
    [ -z "$found" ] && found="$apk"
  fi
done <<< "$art_ids"

if [ -z "$found" ]; then
  echo "::error::运行 $run_id 的产物中没有 .apk"; exit 1
fi

cp -f "$found" "$out_apk"
echo "✅ 已获取同版本官方管理器: $out_apk"

if [ -n "$extract_dir" ]; then
  mkdir -p "$extract_dir"
  for abi in arm64-v8a armeabi-v7a x86_64; do
    mkdir -p "$extract_dir/$abi"
    unzip -o -j "$out_apk" "lib/$abi/libksud.so" -d "$extract_dir/$abi" >/dev/null 2>&1 || true
  done
  echo "已解出 libksud.so -> $extract_dir"
fi
