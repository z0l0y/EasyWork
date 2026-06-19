@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════╗
echo ║     EasyWork 技能包安装脚本 (Windows)        ║
echo ║     v2.1 — AI 全链路开发工作流               ║
echo ╚══════════════════════════════════════════════╝
echo.

:: ============================================
:: 第1步：检测目标项目
:: ============================================
echo [1/4] 检测目标项目...

set "TARGET_DIR="

:: 如果传入了参数，使用参数作为目标目录
if not "%~1"=="" (
    set "TARGET_DIR=%~1"
    goto :check_target
)

:: 否则检测当前目录
set "TARGET_DIR=%CD%"

:check_target
if not exist "%TARGET_DIR%" (
    echo [错误] 目标目录不存在: %TARGET_DIR%
    echo 用法: install.bat [目标项目路径]
    echo 示例: install.bat D:\my-project
    pause
    exit /b 1
)

echo   目标项目: %TARGET_DIR%

:: ============================================
:: 第2步：创建技能目录
:: ============================================
echo [2/4] 创建技能目录...

set "SKILLS_DIR=%TARGET_DIR%\.claude\skills"
set "EASYWORK_SKILLS=%SKILLS_DIR%\easywork"

if not exist "%SKILLS_DIR%" (
    mkdir "%SKILLS_DIR%"
    echo   创建: %SKILLS_DIR%
)

if exist "%EASYWORK_SKILLS%" (
    echo   [警告] easywork 目录已存在，将覆盖更新
    rmdir /s /q "%EASYWORK_SKILLS%"
)

mkdir "%EASYWORK_SKILLS%"
echo   创建: %EASYWORK_SKILLS%

:: ============================================
:: 第3步：复制技能文件
:: ============================================
echo [3/4] 复制技能文件...

set "SOURCE_DIR=%~dp0skills"

:: 复制编排中枢
xcopy /e /i /q "%SOURCE_DIR%\fullchain-dev-workflow" "%EASYWORK_SKILLS%\fullchain-dev-workflow"
if errorlevel 1 (
    echo   [错误] 复制编排中枢失败
    pause
    exit /b 1
)
echo   ✓ fullchain-dev-workflow (编排中枢)

:: 复制9个子技能
for %%s in (read-requirements code-implement code-review examine-quality git-split-commit graph-fullchain sum-session talk-retro ask-change-questions) do (
    xcopy /e /i /q "%SOURCE_DIR%\%%s" "%EASYWORK_SKILLS%\%%s"
    if errorlevel 1 (
        echo   [错误] 复制 %%s 失败
    ) else (
        echo   ✓ %%s
    )
)

:: 复制根文件
copy /y "%~dp0SKILL.md" "%EASYWORK_SKILLS%\SKILL.md" >nul 2>&1
copy /y "%~dp0README.md" "%EASYWORK_SKILLS%\README.md" >nul 2>&1
copy /y "%~dp0QUICKREF.md" "%EASYWORK_SKILLS%\QUICKREF.md" >nul 2>&1

:: ============================================
:: 第4步：更新项目 CLAUDE.md
:: ============================================
echo [4/4] 更新项目 CLAUDE.md...

set "CLAUDE_MD=%TARGET_DIR%\CLAUDE.md"
set "EASYWORK_BLOCK=# EasyWork 全链路工作流"

:: 检查是否已有 EasyWork 配置
if exist "%CLAUDE_MD%" (
    findstr /c:"EasyWork" "%CLAUDE_MD%" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [跳过] CLAUDE.md 已包含 EasyWork 配置
        goto :done
    )
)

:: 追加 EasyWork 配置
(
    echo.
    echo %EASYWORK_BLOCK%
    echo 当用户需要进行代码开发、Bug 修复、代码审查或需求分析时，
    echo 加载 .claude/skills/easywork/fullchain-dev-workflow/SKILL.md
    echo 并严格遵循其任务分类与流程编排规则。
    echo.
    echo ## 可单独调用的子技能
    echo - 需求理解: .claude/skills/easywork/read-requirements/SKILL.md
    echo - 代码实现: .claude/skills/easywork/code-implement/SKILL.md
    echo - 代码审查: .claude/skills/easywork/code-review/SKILL.md
    echo - 质量验证: .claude/skills/easywork/examine-quality/SKILL.md
    echo - 提交拆分: .claude/skills/easywork/git-split-commit/SKILL.md
    echo - 图表绘制: .claude/skills/easywork/graph-fullchain/SKILL.md
    echo - 总结报告: .claude/skills/easywork/sum-session/SKILL.md
    echo - 深度复盘: .claude/skills/easywork/talk-retro/SKILL.md
    echo - 人工确认: .claude/skills/easywork/ask-change-questions/SKILL.md
) >> "%CLAUDE_MD%"
echo   ✓ 已向 CLAUDE.md 追加 EasyWork 配置

:done
:: ============================================
:: 验证安装
:: ============================================
echo.
echo ╔══════════════════════════════════════════════╗
echo ║           安装完成！                         ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 安装位置: %EASYWORK_SKILLS%
echo.
echo 快速验证:
echo   在项目目录中发起 Claude Code 会话，输入：
echo   "帮我 review 下这段代码"
echo   如果 Agent 加载了 code-review 技能并开始审查，则安装成功。
echo.
echo 故障排查: 见 EasyWork 包目录下的 TROUBLESHOOTING.md
echo.
pause
