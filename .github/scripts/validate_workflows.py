#!/usr/bin/env python3
# ===== 说明：校验 .github/workflows 下的工作流 YAML =====
# 来源：WildKernels/GKI_KernelSU_SUSFS 的 .github/scripts/validate_workflows.py
# 作用：解析每个工作流，检查是否包含 jobs、每个 job 是否有 runs-on/uses、每个 step 是否有 run/uses

import pathlib
import sys

import yaml

WORKFLOW_DIR = pathlib.Path(".github/workflows")


def find_workflow_files():
    if not WORKFLOW_DIR.exists():
        return []
    return sorted(list(WORKFLOW_DIR.glob("*.yml")) + list(WORKFLOW_DIR.glob("*.yaml")))


def check_jobs(data):
    errors = []
    jobs = data.get("jobs")

    if jobs is None:
        errors.append("缺少顶层 'jobs'")
        return errors
    if not isinstance(jobs, dict) or not jobs:
        errors.append("'jobs' 必须是非空映射")
        return errors

    for job_name, job in jobs.items():
        if not isinstance(job, dict):
            errors.append(f"job '{job_name}'：必须是映射")
            continue
        if "runs-on" not in job and "uses" not in job:
            errors.append(f"job '{job_name}'：缺少 'runs-on'（可复用工作流用 'uses'）")

        steps = job.get("steps")
        if steps is None:
            if "uses" not in job:
                errors.append(f"job '{job_name}'：缺少 'steps'")
            continue
        if not isinstance(steps, list):
            errors.append(f"job '{job_name}'：'steps' 必须是列表")
            continue
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                errors.append(f"job '{job_name}' 第 {index} 步：必须是映射")
                continue
            if "run" not in step and "uses" not in step:
                name = step.get("name", f"step {index}")
                errors.append(f"job '{job_name}' 的 '{name}'：缺少 'run' 或 'uses'")
    return errors


def check_file(path):
    errors = []
    try:
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except yaml.YAMLError as error:
        mark = getattr(error, "problem_mark", None)
        if mark is not None:
            errors.append(f"YAML 错误（行 {mark.line + 1}, 列 {mark.column + 1}）：{error}")
        else:
            errors.append(f"YAML 错误：{error}")
        return errors

    if not isinstance(data, dict):
        errors.append("顶层不是映射")
        return errors
    # PyYAML 会把未加引号的 on 解析为布尔 True（YAML 1.1）
    if "on" not in data and True not in data:
        errors.append("缺少顶层 'on' 触发键")
    errors.extend(check_jobs(data))
    return errors


def main():
    files = find_workflow_files()
    if not files:
        print(f"未找到工作流文件：{WORKFLOW_DIR}")
        return 0
    status = 0
    for path in files:
        errors = check_file(path)
        if errors:
            status = 1
            print(f"问题文件：{path}")
            for error in errors:
                print(f"  {error}")
    print(f"已检查 {len(files)} 个工作流文件。")
    return status


if __name__ == "__main__":
    sys.exit(main())
