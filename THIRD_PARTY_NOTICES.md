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

`ntsync/patches/` 下的两个 lockdep 前置补丁取自 WildKernels/kernel_patches（GPL-3.0-or-later）。
