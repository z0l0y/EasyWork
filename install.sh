#!/usr/bin/env bash
set -euo pipefail

# EasyWork 技能包安装脚本 (Unix/Linux/macOS)
# v2.4 — AI 全链路开发工作流
#
# 用法:
#   ./install.sh                                    # 安装到当前目录，L3 完整级别
#   ./install.sh --level L2                         # 安装 L2 标准级别
#   ./install.sh --level L1 /path/to/project        # 安装 L1 入门级别到指定项目
#   ./install.sh --uninstall /path/to/project        # 卸载

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║     EasyWork 技能包安装脚本 (Unix)           ║${RESET}"
echo -e "${BOLD}║     v2.2 — AI 全链路开发工作流               ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════╝${RESET}"
echo ""

# ============================================
# 处理 --uninstall
# ============================================
if [ "${1:-}" = "--uninstall" ]; then
    TARGET_DIR="${2:-${PWD}}"
    EASYWORK_SKILLS="${TARGET_DIR}/.claude/skills/easywork"

    if [ ! -d "$EASYWORK_SKILLS" ]; then
        echo -e "${YELLOW}[跳过] EasyWork 未安装在此项目中${RESET}"
        exit 0
    fi

    echo -e "${YELLOW}[卸载] 将删除: ${EASYWORK_SKILLS}${RESET}"
    echo -e "  此操作不可逆。是否继续？[y/N]"
    read -r CONFIRM
    if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
        echo -e "  卸载已取消。"
        exit 0
    fi
    rm -rf "$EASYWORK_SKILLS"
    echo -e "${GREEN}✓ 卸载完成${RESET}"
    echo ""
    echo "如需从 CLAUDE.md 中移除 EasyWork 配置，请手动编辑该文件。"
    echo "（查找 '# EasyWork 全链路工作流' 段落并删除。）"
    exit 0
fi

# ============================================
# 解析参数
# ============================================
LEVEL="L3"
TARGET_DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --level|-l)
            LEVEL="$2"
            shift 2
            ;;
        *)
            TARGET_DIR="$1"
            shift
            ;;
    esac
done

TARGET_DIR="${TARGET_DIR:-${PWD}}"

# 验证 level
case "$LEVEL" in
    L1|L2|L3) ;;
    *)
        echo -e "${RED}[错误] 无效的级别: ${LEVEL}。可选: L1, L2, L3${RESET}"
        echo "用法: ./install.sh [--level L1|L2|L3] [目标项目路径]"
        exit 1
        ;;
esac

# ============================================
# 第1步：检测目标项目
# ============================================
echo -e "${BOLD}[1/4]${RESET} 检测目标项目..."

if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}[错误] 目标目录不存在: ${TARGET_DIR}${RESET}"
    exit 1
fi

TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"
echo "  目标项目: ${TARGET_DIR}"
echo "  成熟度级别: ${LEVEL}"

# ============================================
# 第2步：创建技能目录
# ============================================
echo -e "${BOLD}[2/4]${RESET} 创建技能目录..."

SKILLS_DIR="${TARGET_DIR}/.claude/skills"
EASYWORK_SKILLS="${SKILLS_DIR}/easywork"

mkdir -p "$SKILLS_DIR"

if [ -d "$EASYWORK_SKILLS" ]; then
    echo -e "  ${YELLOW}[警告] easywork 目录已存在${RESET}"
    echo -e "  现有安装包含以下文件："
    find "$EASYWORK_SKILLS" -type f | head -20 | while read -r f; do
        echo "    - ${f#$EASYWORK_SKILLS/}"
    done
    if [ -d "$EASYWORK_SKILLS/custom" ]; then
        echo -e "  ${RED}⚠ 检测到自定义步骤目录 (custom/)，覆盖将永久删除自定义步骤！${RESET}"
    fi
    echo ""
    echo -e "  继续安装将${RED}删除${RESET}以上所有文件。是否继续？[y/N]"
    read -r CONFIRM
    if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
        echo -e "  ${YELLOW}安装已取消。${RESET}"
        exit 0
    fi
    rm -rf "$EASYWORK_SKILLS"
fi

mkdir -p "$EASYWORK_SKILLS"

# ============================================
# 第3步：复制技能文件（按级别）
# ============================================
echo -e "${BOLD}[3/4]${RESET} 复制技能文件（级别: ${LEVEL}）..."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/skills"

# 编排中枢（所有级别必须）
cp -r "${SOURCE_DIR}/fullchain-dev-workflow" "${EASYWORK_SKILLS}/"
echo -e "  ${GREEN}✓${RESET} fullchain-dev-workflow (编排中枢)"

# L1 核心
for skill in read-requirements code-implement code-review; do
    cp -r "${SOURCE_DIR}/${skill}" "${EASYWORK_SKILLS}/"
    echo -e "  ${GREEN}✓${RESET} ${skill}"
done

# L2 额外
if [ "$LEVEL" != "L1" ]; then
    for skill in examine-quality git-split-commit sum-session; do
        cp -r "${SOURCE_DIR}/${skill}" "${EASYWORK_SKILLS}/"
        echo -e "  ${GREEN}✓${RESET} ${skill}"
    done
fi

# L3 额外
if [ "$LEVEL" = "L3" ]; then
    for skill in graph-fullchain talk-retro ask-change-questions; do
        cp -r "${SOURCE_DIR}/${skill}" "${EASYWORK_SKILLS}/"
        echo -e "  ${GREEN}✓${RESET} ${skill}"
    done
fi

# 复制根文件
cp "${SCRIPT_DIR}/SKILL.md" "${EASYWORK_SKILLS}/SKILL.md" 2>/dev/null || true
cp "${SCRIPT_DIR}/README.md" "${EASYWORK_SKILLS}/README.md" 2>/dev/null || true
cp "${SCRIPT_DIR}/QUICKREF.md" "${EASYWORK_SKILLS}/QUICKREF.md" 2>/dev/null || true
echo -e "  ${GREEN}✓${RESET} 根文件（SKILL.md + README.md + QUICKREF.md）"

# ============================================
# 第4步：更新项目 CLAUDE.md
# ============================================
echo -e "${BOLD}[4/4]${RESET} 更新项目 CLAUDE.md..."

CLAUDE_MD="${TARGET_DIR}/CLAUDE.md"

if [ -f "$CLAUDE_MD" ] && grep -q "EasyWork" "$CLAUDE_MD" 2>/dev/null; then
    echo -e "  ${YELLOW}[跳过] CLAUDE.md 已包含 EasyWork 配置${RESET}"
else
    # 备份 CLAUDE.md
    if [ -f "$CLAUDE_MD" ]; then
        cp "$CLAUDE_MD" "${CLAUDE_MD}.bak.$(date +%Y%m%d_%H%M%S)"
        echo -e "  ${GREEN}✓${RESET} 已备份 CLAUDE.md → CLAUDE.md.bak.{timestamp}"
    fi

    cat >> "$CLAUDE_MD" << EOF

# EasyWork 全链路工作流 (v2.4, ${LEVEL}级)
当用户需要进行代码开发、Bug 修复、代码审查或需求分析时，
加载 .claude/skills/easywork/fullchain-dev-workflow/SKILL.md
并严格遵循其任务分类与流程编排规则。

## 可单独调用的子技能
- 需求理解: .claude/skills/easywork/read-requirements/SKILL.md
- 代码实现: .claude/skills/easywork/code-implement/SKILL.md
- 代码审查: .claude/skills/easywork/code-review/SKILL.md
EOF

    if [ "$LEVEL" != "L1" ]; then
        cat >> "$CLAUDE_MD" << 'EOF'
- 质量验证: .claude/skills/easywork/examine-quality/SKILL.md
- 提交拆分: .claude/skills/easywork/git-split-commit/SKILL.md
- 总结报告: .claude/skills/easywork/sum-session/SKILL.md
EOF
    fi

    if [ "$LEVEL" = "L3" ]; then
        cat >> "$CLAUDE_MD" << 'EOF'
- 图表绘制: .claude/skills/easywork/graph-fullchain/SKILL.md
- 深度复盘: .claude/skills/easywork/talk-retro/SKILL.md
- 人工确认: .claude/skills/easywork/ask-change-questions/SKILL.md
EOF
    fi

    echo -e "  ${GREEN}✓${RESET} 已向 CLAUDE.md 追加 EasyWork 配置 (${LEVEL}级)"
fi

# ============================================
# 验证安装
# ============================================
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║           安装完成！ ${LEVEL} 级             ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════╝${RESET}"
echo ""
echo "安装位置: ${EASYWORK_SKILLS}"
echo "成熟度级别: ${LEVEL}"
echo ""

FILE_COUNT=$(find "$EASYWORK_SKILLS" -type f | wc -l | tr -d ' ')
echo "已安装文件数: ${FILE_COUNT}"

echo ""
echo "快速验证:"
echo "  在项目目录中发起 Claude Code 会话，输入："
echo "  \"帮我 review 下这段代码\""
echo "  如果 Agent 加载了 code-review 技能并开始审查，则安装成功。"
echo ""
echo "升级级别: 再次运行 ./install.sh --level L2 (或 L3)"
echo "故障排查: 见 EasyWork 包目录下的 TROUBLESHOOTING.md"
echo ""
