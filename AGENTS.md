# AGENTS.md — SukiSU 构建规则

## 1. 核心目标

根据用户指定的 SukiSU 版本，构建：

- 对应版本的 Kernel/SukiSU
- 对应版本的 AnyKernel3 刷机包
- 对应版本的 SukiSU Manager
- 用户指定的额外功能
- 最终可验证、可刷写的完整产物

**用户指定的版本永远优先于最新版。禁止擅自升级。**

---

## 2. 版本锁定

开始任何修改、下载、编译前，必须先确认：

```text
SukiSU version
SukiSU commit
Kernel commit
Manager commit
AnyKernel3 commit
ksud version
KPM version
SUSFS version
额外功能版本
Android version
Kernel version
Target device
Architecture
```

优先锁定 commit，而不是使用浮动 branch。

必须建立 `VERSION_LOCK.md` 记录所有实际使用版本。

---

## 3. 严禁跨版本混用

默认禁止：

```text
旧 SukiSU + 新 AnyKernel3
旧 SukiSU + 新 Manager
旧 ksud + 新 Manager
旧 Kernel API + 新功能实现
旧 SukiSU + 新版 KPM/SUSFS
```

**不能证明兼容 = 默认不兼容。**

不要因为“最新版应该兼容”就直接使用最新版。

---

## 4. AnyKernel3 规则

AnyKernel3 必须与用户指定的 SukiSU 版本和目标设备安装机制匹配。

必须检查：

```text
anykernel.sh
boot/vendor_boot/init_boot
Image/Image.gz/Image.gz-dtb
dtb/dtbo
slot 逻辑
设备检查
ramdisk 处理
SukiSU 安装逻辑
KPM/SUSFS 相关逻辑
```

禁止直接拿最新版 AnyKernel3 强行套旧版 SukiSU。

如果 AnyKernel3 版本不同，必须证明：

```text
API 兼容
安装流程兼容
镜像处理兼容
功能行为兼容
```

否则使用目标版本对应的实现。

---

## 5. 额外功能规则

加入 KPM、SUSFS、Manual Hook、其他 Kernel Patch 或自定义功能时，必须确认：

```text
目标版本
API
ABI
函数签名
结构体
CONFIG
Hook 位置
调用链
userspace 接口
Manager 接口
```

禁止直接复制新版本代码到旧版本。

如果需要 backport：

```text
旧实现
↓
新实现
↓
源码/API 差异
↓
确认可 backport
↓
最小修改
↓
编译验证
```

---

## 6. Manager 规则

Manager 必须与目标 SukiSU 版本对应。

禁止为了编译成功：

- 修改版本号伪装兼容
- 修改 API 检查绕过版本限制
- 使用未经验证的新 Manager
- 用新接口强行适配旧 Kernel

必须检查：

```text
Manager version
versionCode
API version
ksud 通信
KPM 通信
SUSFS 通信
root 通信
```

---

## 7. 自动重新思考触发器

出现以下任意情况，**立即停止当前操作并重新分析**：

```text
版本不一致
API 不一致
ABI 不一致
函数不存在
函数参数变化
结构体变化
CONFIG 不存在
unknown symbol
undefined reference
implicit declaration
no member named
Manager/API mismatch
AnyKernel3 与设备不匹配
boot/vendor_boot/init_boot 处理异常
Image/dtb/dtbo 处理异常
```

触发后必须执行：

```text
STOP
↓
记录错误
↓
确认目标版本
↓
确认实际版本
↓
源码/API 对比
↓
判断是否版本错配
↓
重新设计
↓
再修改
↓
再编译
```

**禁止出现“报错 → 乱改 → 再编译 → 再报错”的循环。**

---

## 8. 禁止为了编译成功而修改

禁止：

```text
删除报错代码
随意注释功能
关闭检查
伪造版本号
绕过兼容性判断
用新代码覆盖旧代码
```

编译成功不是最终目标。

最终目标是：

> **目标 SukiSU 版本的正确实现 + 正确 AnyKernel3 + 正确 Manager + 正确额外功能。**

---

## 9. 编译前一致性检查

正式编译前必须确认：

```text
Target SukiSU:
Kernel:
Manager:
AnyKernel3:
ksud:
KPM:
SUSFS:
Android:
Kernel:
Device:
Architecture:

Version compatibility: PASS/FAIL
API compatibility: PASS/FAIL
AnyKernel compatibility: PASS/FAIL
Feature compatibility: PASS/FAIL
```

任何一项 FAIL：

**禁止正式构建。**

---

## 10. 编译失败分类

编译失败必须先判断属于：

```text
环境
工具链
Kernel
SukiSU 版本
API
SUSFS
KPM
AnyKernel3
Manager
设备适配
```

不能默认认为“改代码就能解决”。

---

## 11. Git 规则

修改前必须执行：

```bash
git status
git branch
git rev-parse HEAD
git remote -v
```

记录 baseline commit。

重要修改必须能够通过：

```bash
git diff
```

解释清楚。

下载源码后必须确认：

```bash
git rev-parse HEAD
git describe --tags --always
```

禁止直接使用未知状态的 main/master。

---

## 12. 最终产物

最终至少生成：

```text
output/
├── SukiSU-<VERSION>-<DEVICE>-AnyKernel3.zip
├── SukiSU-<VERSION>-Manager.apk
├── VERSION_LOCK.md
├── BUILD_INFO.txt
└── SHA256SUMS
```

最终必须检查：

```text
ZIP 可解压
脚本存在
脚本权限正确
Image 正确
boot 处理正确
slot 正确
设备判断正确
Manager 可安装
版本一致
```

---

## 13. 代码注释与汉化（强制）

移植 / 新增任何代码（工作流、composite action、脚本、补丁说明）时必须：

- **中文注释**：文件顶部写中文说明；关键逻辑（版本约束、为什么这么改、坑点）逐段加中文注释。
- **汉化**：面向用户的文案一律中文 —— workflow / step 的 `name`、`description`、artifact 名、日志提示、错误信息。
- **保留英文**：变量名、Kconfig、命令、API、分支/标签、镜像名等**技术标识不要翻译**，以免破坏功能。
- **移植留痕**：从其他项目（ABK / WildKernels / SukiSU 官方等）搬代码时，除注释与汉化外，必须写明**来源**与**版本对应关系**。

---

## 14. 最高优先级规则

永远遵守：

> **版本优先、证据优先、最小修改、禁止猜测、禁止强行兼容。**

遇到不确定：

```text
STOP → RETHINK → VERIFY → MODIFY → BUILD
```

而不是：

```text
MODIFY → BUILD → ERROR → MODIFY → BUILD
```

**OpenCode 不得自行改变用户指定的 SukiSU 版本。**

**OpenCode 不得为了方便使用新版本替代旧版本。**

**无法证明兼容性时，必须停止并重新分析。**
