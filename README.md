# aaa-neihe

Android GKI 内核自动化构建（GitHub Actions）。基于 [jiuxiao226/KernelSU-Actions](https://github.com/jiuxiao226/KernelSU-Actions) 的结构重写，加入模块化的功能开关，并参考 [xingguangcuican6666/ABK](https://github.com/xingguangcuican6666/ABK) 的功能清单。

产物为 **AnyKernel3 ZIP** 与可选的 **boot 镜像**，可直接在 Recovery / 内核刷写工具中刷入。

---

## 目录结构

```
.github/
├─ actions/                     # 模块化功能（composite actions）
│  ├─ setup-env/                # 初始化路径 / repo 工具
│  ├─ set-kernel-config/        # 幂等写入 gki_defconfig
│  ├─ root-setup/               # KernelSU 变体 + 分支/Tag + KSU_VERSION
│  ├─ susfs/                    # SUSFS 补丁 + Unicode 修复 + 配置
│  ├─ zram/                     # ZRAM 增强 + 完整算法（6.12 自动跳过）
│  ├─ bbg/                      # BBG 防格机
│  ├─ ddk/                      # DDK（xingguang-ddk）防格机 LSM
│  ├─ ntsync/                   # NTsync
│  ├─ networking/               # 网络增强（IPSet + BBR）
│  ├─ rekernel/                 # Re-Kernel 驱动
│  └─ kpm/                      # KPM 镜像补丁（编译后）
├─ matrix/
│  ├─ versions.tsv             # GKI 矩阵版本表（android|kernel|sub|patch|revision）
│  └─ nongki.tsv               # 非 GKI 批量 profile 表（name|series|arch|source|branch|defconfig|image）
├─ nongki/
│  └─ legacy_ksu_hooks.sh      # 4.x/5.4 手动 hook 补丁（KernelSU 上游）
└─ workflows/
   ├─ build-kernel.yml          # GKI 构建入口（workflow_dispatch / workflow_call）
   ├─ matrix-build.yml          # GKI 矩阵构建入口
   ├─ non-gki-build.yml         # 非 GKI（4.x / 5.4）构建入口（可复用 workflow_call）
   └─ non-gki-matrix.yml        # 非 GKI 批量构建入口
```

---

## 使用方法

1. Fork / 使用本仓库。
2. 打开 **Actions → 内核构建流程 → Run workflow**。
3. 填好参数（见下），运行。
4. 构建完成后在本次运行的 **Artifacts** 下载 `*AnyKernel3.zip`。

---

## 选项说明

### 基础配置
| 选项 | 说明 |
|---|---|
| `android_version` | `android12 ~ android16` |
| `kernel_version` | `5.10 / 5.15 / 6.1 / 6.6 / 6.12` |
| `sub_level` | 子版本号（**留空=自动取该组合最新一档**） |
| `os_patch_level` | 补丁级别（**留空=自动跟随子版本**） |
| `revision` | Android 12 GKI 修订号（仅 `android12` 用），如 `r1` |

### KernelSU / 管理器
| 选项 | 说明 |
|---|---|
| `ksu_variant` | `SukiSU / Official / ReSukiSU / Next / None` |
| `ksu_branch` | `Stable(标准) / Dev(开发) / Latest(最新) / Other(其他/指定)` |
| `custom_ref` | 自定义管理器 **分支或 Tag**（上一步选“其他/指定”时生效） |
| `ksu_version` | 强制写入内核 `KSU_VERSION`（留空=源码默认；**例如填 `13000` 即 sukisu13000**） |

> **指定管理器版本**的两种方式：
> 1. 想让内核带上某个 SukiSU 分支/Tag → `ksu_branch = Other(其他/指定)` + `custom_ref = main / builtin / v4.2.0`。
> 2. 想让内核上报固定版本号（与管理器 APK 匹配）→ 填 `ksu_version`，例如 `13000`。

### 功能开关
| 选项 | 说明 | 来源 |
|---|---|---|
| `use_susfs` | SUSFS Root 隐藏 | simonpunk / ShirkNeko `susfs4ksu` |
| `use_zram` | ZRAM 增强算法（LZ4 升级 + NEON） | ABK `zram/` 资产 |
| `zram_full_algo` | ZRAM 完整算法（LZ4K / LZ4KD / LZ4K_OPLUS，**6.12 自动跳过**） | ShirkNeko `SukiSU_patch` |
| `zram_extra_algos` | 额外算法（如 `lzo,lz4,deflate,zstd,842`） | 内核 crypto 配置 |
| `use_bbg` | BBG 防格机 | `vc-teahouse/Baseband-guard` |
| `use_ddk` | DDK 防格机 LSM | ABK `xingguang-ddk` |
| `use_ntsync` | NTsync | `WildKernels/kernel_patches` |
| `use_networking` | 网络增强（IPSet + BBR + qdisc + WireGuard + CIFS） | 内核配置 |
| `use_kpm` | KPM 功能（**仅 SukiSU / ReSukiSU**） | `SukiSU_patch/kpm` |
| `kpm_password` | 自定义 KPM 超级密码 | — |
| `use_rekernel` | Re-Kernel 驱动 | `Sakion-Team/Re-Kernel` |

### 高级配置
| 选项 | 说明 |
|---|---|
| `version` | 自定义内核后缀字符串 |
| `build_time` | 自定义构建时间（留空=当前 UTC） |
| `custom_kernel_options` | 自定义 defconfig 片段（每行一条） |
| `publish_release` | 构建完成后把产物发布到 GitHub Releases（tag 形如 `android14-6.1.145-2025-09-SukiSU-r<运行号>`） |
| `upload_manager` | 同时下载并上传对应版本的管理器 APK（默认开；产物里会多一个 `SukiSU/...apk`） |

---

## 管理器重命名（默认 `w.fkiu`）

构建时会自动：下载对应变体的管理器 → 用 apktool 改包名 → 重新签名 → 把新签名注入内核（这样重签名后的管理器仍能拿到 root）。

| 仓库变量 | 作用 | 默认 |
|---|---|---|
| `MANAGER_PACKAGE` | 目标包名 | `w.fkiu` |
| `MANAGER_RENAME` | 设为 `false` 可关闭改名（只下载官方管理器） | 开 |
| `MANAGER_KEYSTORE_B64` | 自定义 keystore（base64） | 留空=每次随机生成（同一次产物自洽） |
| `MANAGER_KEYSTORE_PASS` | keystore 口令 | `android` |

原理：
- **SukiSU / ReSukiSU**：可接受的管理器签名写死在 `apk_sign.c` 的 `apk_sign_keys[]` 数组里 → 构建时把 `{size,hash}` 插进去。
- **tiann/KernelSU**：用 `KSU_EXPECTED_SIZE` / `KSU_EXPECTED_HASH` → 构建时替换其默认值。
- 若源码支持 `KSU_MANAGER_PACKAGE`，同时把期望包名设为 `MANAGER_PACKAGE`。

> 单独测试重打包：工作流 **`管理器重打包（改包名）`**（`.github/workflows/manager-repack.yml`）。

---

## 矩阵构建

工作流 **`矩阵内核构建`**（`.github/workflows/matrix-build.yml`）可按范围一次扇出多个内核构建。版本表在 **`.github/matrix/versions.tsv`**。

### 范围选择
| 输入 | 说明 |
|---|---|
| `kernel_scope` | `全部` / `5系列` / `6系列` / `5.10` / `5.15` / `6.1` / `6.6` / `6.12` |
| `android_scope` | `全部` 或指定单个 Android（主要给 5.x 用） |
| `sub_version_mode` | `最新子版本`（每组合取最新一档）/ `全部子版本` |

常用例子：
| 想要的效果 | 选择 | 目标数 |
|---|---|---|
| **只构建 6.1 的全部子版本** | `kernel_scope=6.1` + `全部子版本` | 24 |
| 只构建 6.1 的最新一档 | `kernel_scope=6.1` + `最新子版本` | 1 |
| 6 系列全部子版本 | `6系列` + `全部子版本` | 49 |
| 5 系列全部子版本 | `5系列` + `全部子版本` | 87 |
| 全部版本 × 全部子版本 | `全部` + `全部子版本` | 136 |
| 每版本最新（默认） | `全部` + `最新子版本` | 7 |

> 不再需要另填 `android/kernel/sub` 等字段——选了 `kernel_scope` 就决定了构建哪些。

### 版本表（`versions.tsv`）
格式：`android|kernel|sub_level|os_patch_level|revision`，`#` 开头为注释，`X|lts` 表示 lts 分支（“最新子版本”模式自动忽略）。当前收录：

| 组合 | 档数 | 最新一档 |
|---|---|---|
| android12-5.10 | 24 | 252 / 2026-04 |
| android13-5.10 | 22 | 252 / 2026-04 |
| android13-5.15 | 23 | 206 / 2026-06 |
| android14-5.15 | 18 | 202 / 2026-04 |
| android14-6.1 | 24 | 172 / 2026-06 |
| android15-6.6 | 18 | 139 / 2026-07 |
| android16-6.12 | 7 | 81 / 2026-06 |

> ⚠️ `全部子版本`（尤其 `全部版本` + `全部子版本`）会一次排入大量构建，非常耗时/耗额度；建议先单个组合验证通过。

> 其余选项与单次构建一致，会透传给 `build-kernel.yml`。开启 `publish_release` 时每个目标各自发一个 Release。

---

## 4 系列（非 GKI）特别说明

> ⚠️ 4.x 与 GKI（5.10+）**完全不同**：没有 AOSP 通用源码，**必须自备设备内核源码**。工作流 `非 GKI 内核构建（4.x / 5.4）`（`.github/workflows/non-gki-build.yml`）用 `make` + AOSP Clang 构建，与上面的 GKI 流程相互独立。

### 你需要提供的
| 输入 | 说明 |
|---|---|
| `kernel_source` / `kernel_source_branch` | 设备内核仓库与分支 |
| `defconfig` | `arch/<arch>/configs/` 下的 defconfig 路径（可含子目录，如 `vendor/wayne_defconfig`） |
| `image_name` | 产物名，如 `Image.gz-dtb` / `Image.gz` / `Image` |
| `arch` | `arm64` 或 `arm` |
| `kernel_series` | `4.4 / 4.9 / 4.14 / 4.19 / 5.4`，决定默认工具链与 KSU ref |

### 工具链（自动）
| 系列 | Clang | binutils |
|---|---|---|
| 4.4 / 4.9 / 4.14 / 4.19 | AOSP `master-kernel-build-2022` / `r450784e` | GCC 4.9（aarch64 + arm） |
| 5.4 | AOSP `main-kernel-build-2024` / `r510928` | GCC 4.9 |

> 新 Clang 常无法编译 4.x（旧语法/更严警告），因此默认锁在 `r450784e`；`clang_branch` / `clang_version` 可手动覆盖，`use_llvm=true` 通常只适合 5.x。

### KernelSU
| 变体 | 默认 ref | 说明 |
|---|---|---|
| `resukisu`（推荐） | `main` | 面向老内核/非 GKI |
| `sukisu-ultra` | `builtin` | 自带 SUSFS |
| `kernelsu` | `v0.9.5`（<5.10） | 官方自 v1.0 起不再支持非 GKI |
| `kernelsu-next` | `legacy`（<5.10） | 老内核用 `legacy` |
| `none` | — | 不集成 root |

**hook 方式**：4.x 上 `kprobes` 经常「装上了但 su 无反应」，所以 `hook_mode=auto` 在老内核会自动改用手动 hook，由 `.github/nongki/legacy_ksu_hooks.sh` 往 `fs/exec.c`、`fs/open.c`、`fs/read_write.c`、`fs/stat.c`、`drivers/input/input.c` 注入 syscall hook（逻辑源自 KernelSU 上游，GPL-3.0）。

### SUSFS（实验性，默认关闭）
- 仅 `4.9 / 4.14 / 4.19 / 5.4` 有非 GKI 分支（`kernel-4.9` 等）；**4.4 无**。
- susfs4ksu 的非 GKI 分支自 2025 初起基本未更新，可能因内核树差异而打补丁失败；失败会中止构建，可关闭 `use_susfs` 重试。
- 更稳的组合是 `ksu_variant=sukisu-ultra` + `ksu_ref=builtin`（自带 SUSFS）。

### 目前未包含
- `boot.img` 重打包（需要与设备/ROM 匹配的原始 boot 镜像，且分区结构各异）。
- DTBO **生成**（`need_dtbo=true` 只是把已生成的 `dtbo.img` 一起打包）。
- 非 GKI 的 KPM（`patch_linux` 对老内核支持不稳定）。

### 示例
默认值即为一个可跑通的 4.19 组合（来自 xiaoleGun 的示例设备）：
```
kernel_series=4.19
kernel_source=https://github.com/xiaoleGun/android_kernel_xiaomi_wayne-4.19
kernel_source_branch=twrp-12
defconfig=vendor/wayne_defconfig
image_name=Image.gz-dtb
```
> 换你自己的设备时，把上面四项改成你的内核仓库/分支/defconfig/产物名即可。

### 批量构建
工作流 **`非 GKI 批量构建`**（`.github/workflows/non-gki-matrix.yml`）读取 **`.github/matrix/nongki.tsv`**，按系列扇出。

- 表格格式：`name|series|arch|source|branch|defconfig|image`，`#` 开头为注释。
- 只有**未注释**的行参与构建；默认启用 `wayne-4.19` 一个 profile，其它系列（4.4/4.9/4.14/5.4）为注释示例，核对 defconfig/分支后取消注释即可。
- 入参 `series` 可只构建某一系列，或 `All` 构建所有启用项。

> 单次构建用 `非 GKI 内核构建（4.x / 5.4）`；要一次跑多个设备/系列用 `非 GKI 批量构建`。

---

## 注意事项

- **ZRAM 完整算法**：`6.12` 使用新式 zram backend，会自动跳过 legacy `LZ4K/LZ4KD/LZ4K_OPLUS` 补丁栈。
- **ZRAM 模块**：若在设备上使用 ZRAM 增强，部分机型需额外刷入 ZRAM 附加模块并在其中选择算法（本仓库不打包该模块）。
- **DDK / ZRAM 资产**：构建时会浅克隆 `xingguangcuican6666/ABK` 以获取 `ddk/` 与 `zram/` 资产；若上游变动可能导致这两项失效。
- **KPM**：仅 `SukiSU` / `ReSukiSU` 支持，其他变体会自动跳过。KPM 在编译完成后对 `Image` 执行 `patch_linux`。
- **Official 变体**：不内置 SUSFS，SUSFS 以补丁方式应用。
- **构建时间**：首次运行因 ccache 未命中可能较慢，后续会显著加快。

---

## 第三方与致谢

见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 许可

本仓库不包含独立的 LICENSE 文件；构建时拉取或参考的各上游组件保留其各自许可，见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
