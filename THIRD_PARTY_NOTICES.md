# THIRD_PARTY_NOTICES

本仓库的构建流程会在运行时拉取/调用以下第三方项目。它们各自保留其原有许可与版权。

| 组件 | 用途 | 来源 |
|---|---|---|
| KernelSU | 官方 Root | https://github.com/tiann/KernelSU |
| SukiSU-Ultra | Root 变体 | https://github.com/SukiSU-Ultra/SukiSU-Ultra |
| ReSukiSU | Root 变体 | https://github.com/ReSukiSU/ReSukiSU |
| KernelSU-Next | Root 变体 | https://github.com/KernelSU-Next/KernelSU-Next |
| susfs4ksu | Root 隐藏 | https://gitlab.com/simonpunk/susfs4ksu · https://github.com/ShirkNeko/susfs4ksu |
| kernel_patches | NTsync / SUSFS 修复 / BBRv3 / 性能补丁 | https://github.com/WildKernels/kernel_patches |
| SukiSU_patch | ZRAM lz4k / KPM / hooks | https://github.com/ShirkNeko/SukiSU_patch |
| Action-Build | Unicode 绕过修复补丁 | https://github.com/Numbersf/Action-Build |
| Baseband-guard | BBG 防格机 LSM | https://github.com/vc-teahouse/Baseband-guard |
| Re-Kernel | Re:Kernel 驱动 | https://github.com/Sakion-Team/Re-Kernel |
| ABK | Xingguang-DDK 防格机 LSM / ZRAM LZ4 升级资产 | https://github.com/xingguangcuican6666/ABK |
| AnyKernel3 | 打包刷机包 | https://github.com/osm0sis/AnyKernel3 · https://github.com/WildKernels/AnyKernel3 |

结构与思路参考：

- https://github.com/jiuxiao226/KernelSU-Actions
- https://github.com/WildKernels/GKI_KernelSU_SUSFS
- https://sukisu.org/zh/guide/links
- https://github.com/xiaoleGun/KernelSU_Action （非 GKI 4.x/5.4 构建思路）
- https://github.com/dabao1955/kernel_build_action （非 GKI 构建思路）

`ntsync/patches/` 下的两个 lockdep 前置补丁取自 WildKernels/kernel_patches（GPL-3.0-or-later）。

`.github/nongki/legacy_ksu_hooks.sh`（非 GKI 手动 hook）源自 KernelSU 官方手动 hook 补丁（作者 weishu <twosxtd@gmail.com>，GPL-3.0），整理为脚本以便在 4.x/5.4 老内核上注入 syscall hook。

非 GKI 构建使用的 SUSFS 非 GKI 分支（`kernel-4.9/4.14/4.19/5.4`）来自 simonpunk/susfs4ksu。
