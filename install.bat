@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════╗
echo ║     EasyWork 技能包安装脚本 (Windows)        ║
echo ║     v2.2 — AI 全链路开发工作流               ║
echo ╚══════════════════════════════════════════════╝
echo.

:: ============================================
:: 解析参数
:: ============================================
set "LEVEL=L3"
set "TARGET_DIR="

:parse_args
if "%~1"=="" goto :args_done
if /i "%~1"=="--level" (
    set "LEVEL=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="-l" (
    set "LEVEL=%~2"
    shift
    shift
    goto :parse_args
)
set "TARGET_DIR=%~1"
shift
goto :parse_args

:args_done
if "%TARGET_DIR%"=="" set "TARGET_DIR=%CD%"

:: 验证 level
if /i "%LEVEL%"=="L1" goto :level_ok
if /i "%LEVEL%"=="L2" goto :level_ok
if /i "%LEVEL%"=="L3" goto :level_ok
echo [错误] 无效的级别: %LEVEL%。可选: L1, L2, L3
echo 用法: install.bat [--level L1^|L2^|L3] [目标项目路径]
pause
exit /b 1

:level_ok
echo [1/4] 检测目标项目...
if not exist "%TARGET_DIR%" (
    echo [错误] 目标目录不存在: %TARGET_DIR%
    pause
    exit /b 1
)
echo   目标项目: %TARGET_DIR%
echo   成熟度级别: %LEVEL%

:: ============================================
:: 第2步：创建技能目录
:: ============================================
echo [2/4] 创建技能目录...

set "SKILLS_DIR=%TARGET_DIR%\.claude\skills"
set "EASYWORK_SKILLS=%SKILLS_DIR%\easywork"

if not exist "%SKILLS_DIR%" mkdir "%SKILLS_DIR%"

if exist "%EASYWORK_SKILLS%" (
    echo   [警告] easywork 目录已存在，将覆盖更新
    rmdir /s /q "%EASYWORK_SKILLS%"
)
mkdir "%EASYWORK_SKILLS%"

:: ============================================
:: 第3步：复制技能文件（按级别）
:: ============================================
echo [3/4] 复制技能文件（级别: %LEVEL%）...

set "SOURCE_DIR=%~dp0skills"

:: 编排中枢（所有级别必须）
xcopy /e /i /q "%SOURCE_DIR%\fullchain-dev-workflow" "%EASYWORK_SKILLS%\fullchain-dev-workflow" >nul 2>&1
if errorlevel 1 (echo   [错误] 编排中枢复制失败 & pause & exit /b 1)
echo   ✓ fullchain-dev-workflow (编排中枢)

:: L1 核心技能
for %%s in (read-requirements code-implement code-review) do (
    xcopy /e /i /q "%SOURCE_DIR%\%%s" "%EASYWORK_SKILLS%\%%s" >nul 2>&1
    echo   ✓ %%s
)

:: L2 额外技能
if /i "%LEVEL%"=="L1" goto :skip_l2
for %%s in (examine-quality git-split-commit sum-session) do (
    xcopy /e /i /q "%SOURCE_DIR%\%%s" "%EASYWORK_SKILLS%\%%s" >nul 2>&1
    echo   ✓ %%s
)
:skip_l2

:: L3 额外技能
if /i "%LEVEL%"=="L1" goto :skip_l3
if /i "%LEVEL%"=="L2" goto :skip_l3
for %%s in (graph-fullchain talk-retro ask-change-questions) do (
    xcopy /e /i /q "%SOURCE_DIR%\%%s" "%EASYWORK_SKILLS%\%%s" >nul 2>&1
    echo   ✓ %%s
)
:skip_l3

:: 复制根文件
copy /y "%~dp0SKILL.md" "%EASYWORK_SKILLS%\SKILL.md" >nul 2>&1
copy /y "%~dp0README.md" "%EASYWORK_SKILLS%\README.md" >nul 2>&1
copy /y "%~dp0QUICKREF.md" "%EASYWORK_SKILLS%\QUICKREF.md" >nul 2>&1
echo   ✓ 根文件（SKILL.md + README.md + QUICKREF.md）

:: ============================================
:: 第4步：更新项目 CLAUDE.md
:: ============================================
echo [4/4] 更新项目 CLAUDE.md...

set "CLAUDE_MD=%TARGET_DIR%\CLAUDE.md"

if exist "%CLAUDE_MD%" (
    findstr /c:"EasyWork" "%CLAUDE_MD%" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [跳过] CLAUDE.md 已包含 EasyWork 配置
        goto :done
    )
)

(
    echo.
    echo # EasyWork 全链路工作流 ^(v2.2, %LEVEL%级^)
    echo 当用户需要进行代码开发、Bug 修复、代码审查或需求分析时，
    echo 加载 .claude/skills/easywork/fullchain-dev-workflow/SKILL.md
    echo 并严格遵循其任务分类与流程编排规则。
    echo.
    echo ## 可单独调用的子技能
    echo - 需求理解: .claude/skills/easywork/read-requirements/SKILL.md
    echo - 代码实现: .claude/skills/easywork/code-implement/SKILL.md
    echo - 代码审查: .claude/skills/easywork/code-review/SKILL.md
) >> "%CLAUDE_MD%"

if /i not "%LEVEL%"=="L1" (
    (
        echo - 质量验证: .claude/skills/easywork/examine-quality/SKILL.md
        echo - 提交拆分: .claude/skills/easywork/git-split-commit/SKILL.md
        echo - 总结报告: .claude/skills/easywork/sum-session/SKILL.md
    ) >> "%CLAUDE_MD%"
)

if /i "%LEVEL%"=="L3" (
    (
        echo - 图表绘制: .claude/skills/easywork/graph-fullchain/SKILL.md
        echo - 深度复盘: .claude/skills/easywork/talk-retro/SKILL.md
        echo - 人工确认: .claude/skills/easywork/ask-change-questions/SKILL.md
    ) >> "%CLAUDE_MD%"
)

echo   ✓ 已向 CLAUDE.md 追加 EasyWork 配置 (%LEVEL%级)

:done
:: ============================================
:: 验证安装
:: ============================================
echo.
echo ╔══════════════════════════════════════════════╗
echo ║           安装完成！ %LEVEL% 级             ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 安装位置: %EASYWORK_SKILLS%
echo 成熟度级别: %LEVEL%
echo.
echo 快速验证:
echo   在项目目录中发起 Claude Code 会话，输入：
echo   "帮我 review 下这段代码"
echo   如果 Agent 加载了 code-review 技能并开始审查，则安装成功。
echo.
echo 升级级别: 再次运行 install.bat --level L2 ^(或 L3^)
echo 故障排查: 见 EasyWork 包目录下的 TROUBLESHOOTING.md
echo.
pause
