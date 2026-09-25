#!/usr/bin/env bash
# ===== 说明：读取 config JSON 矩阵（替代 versions.tsv） =====
# 来源：WildKernels/GKI_KernelSU_SUSFS 的 .github/config/*.json + prepare.yml 读取方式
# 用法：在 run 里 `source "$GITHUB_WORKSPACE/.github/scripts/matrix_config.sh"`
#   数据格式：{ "version": "android14-6.1", "include": [ {sublevel, date, revision?} ] }

# 配置目录（可用 CFG_DIR 覆盖）
cfg_dir() { echo "${CFG_DIR:-$GITHUB_WORKSPACE/.github/config}"; }

# 打印某个 KMI 的配置文件名
cfg_file() { echo "$(cfg_dir)/${1}-${2}.json"; }

# 最新“数字”子版本一行：输出 sub|date|revision
cfg_latest() {
  local A="$1" K="$2" f; f="$(cfg_file "$A" "$K")"
  [ -f "$f" ] || { echo "::error::缺少配置文件 $f" >&2; return 1; }
  jq -r '[.include[] | select(.sublevel|test("^[0-9]+$"))]
         | sort_by(.sublevel|tonumber) | last
         | "\(.sublevel)|\(.date)|\(.revision // "r1")"' "$f"
}

# 指定子版本的补丁级别（date）
cfg_patch() {
  local A="$1" K="$2" S="$3" f; f="$(cfg_file "$A" "$K")"
  [ -f "$f" ] || return 1
  jq -r --arg s "$S" '[.include[] | select(.sublevel==$s)][0].date // empty' "$f"
}

# 输出某 KMI 全部行（TSV 形式：A|K|sub|date|rev），可按正则过滤子版本
cfg_rows() {
  local A="$1" K="$2" f; f="$(cfg_file "$A" "$K")"
  [ -f "$f" ] || { echo "::error::缺少配置文件 $f" >&2; return 1; }
  jq -r --arg a "$A" --arg k "$K" \
    '.include[] | "\($a)|\($k)|\(.sublevel)|\(.date)|\(.revision // "r1")"' "$f"
}

# 列出所有配置文件路径
cfg_all_files() { ls "$(cfg_dir)"/*.json 2>/dev/null; }
