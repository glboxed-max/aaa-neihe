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
│  └─ versions.tsv             # 矩阵版本表（android|kernel|sub|patch|revision）
└─ workflows/
   ├─ build-kernel.yml          # 构建入口（workflow_dispatch / workflow_call）
   └─ matrix-build.yml          # 矩阵构建入口
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
| `sub_level` | 子版本号，如 `145` |
| `os_patch_level` | 补丁级别，如 `2025-09` |
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

---

## 矩阵构建

工作流 **`矩阵内核构建`**（`.github/workflows/matrix-build.yml`）可按范围一次扇出多个内核构建。版本表在 **`.github/matrix/versions.tsv`**。

### 范围选择
| 选项 | 含义 |
|---|---|
| `build_scope` = `全部版本` | 所有 Android 版本 |
| `build_scope` = `5系列` | 只看 5.x 内核（5.10 / 5.15） |
| `build_scope` = `6系列` | 只看 6.x 内核（6.1 / 6.6 / 6.12） |
| `build_scope` = `单独指定` | 只构建下面单独填写的那一个组合 |
| `sub_version_mode` = `最新子版本` | 每个 (Android,内核) 组合只取 **sub_level 最大** 的一档 |
| `sub_version_mode` = `全部子版本` | 取该范围内的**全部**子版本 |

> 「单独指定」时使用 `android_version` / `kernel_version` / `sub_level` / `os_patch_level` / `revision` 五个输入。

### 常用组合
| 想要的效果 | 选择 |
|---|---|
| 每版本最新（默认） | `全部版本` + `最新子版本` → 7 个目标 |
| 全部版本 × 全部子版本 | `全部版本` + `全部子版本` → 136 个目标 |
| 5 系列全部子版本 | `5系列` + `全部子版本` |
| 6 系列全部子版本 | `6系列` + `全部子版本` |
| 只构建一个 | `单独指定` + 填 5 个输入 |

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

本仓库自身的工作流与脚本以 GPL-3.0-or-later 发布；构建时拉取的各上游组件保留其各自许可。
