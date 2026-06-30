# Security Policy

## 支持的版本

| 版本 | 支持状态 |
|------|---------|
| 3.x   | ✅ 活跃支持 |
| 2.x   | ❌ 已停止支持 |
| 1.x   | ❌ 已停止支持 |

## 报告漏洞

EasyWork 项目高度重视安全问题。如果你发现安全漏洞，请**不要**在公开 Issue 中报告。

### 报告流程

1. 发送邮件到项目维护者，描述漏洞详情
2. 包含以下信息：
   - 受影响的版本
   - 漏洞复现步骤
   - 潜在影响范围
   - 建议的修复方案（如有）
3. 我们将在 **48 小时内** 确认收到报告
4. 我们将在 **7 天内** 提供初步评估和修复时间线
5. 修复发布后，我们将在 CHANGELOG 中致谢（除非你要求匿名）

### 漏洞范围

以下类型的问题属于安全漏洞，请报告：

- **MCP Server 安全**：任意代码执行、权限提升、数据泄露
- **Hook 脚本注入**：通过 Skill 文件或配置实现代码注入
- **工具权限绕过**：allowed-tools 限制被绕过或提权
- **敏感信息泄露**：Token/密钥/内部 URL 在产出物中未脱敏
- **供应链攻击**：依赖的 MCP Server 或 npm 包被劫持利用
- **Prompt Injection**：通过用户输入控制 Agent 执行恶意操作

### 非漏洞范围

以下情况**不**被视为安全漏洞：

- 用户自行配置的高权限 allowed-tools（如用户主动添加 `Bash(*)`）
- 用户故意安装的不可信 MCP Server
- `.easywork/config.json` 中的配置项（由用户完全控制）
- 用户自行修改的 Hook 脚本

## 安全设计

EasyWork 的安全模型基于以下原则：

| 原则 | 实现 |
|------|------|
| **最小权限** | Skill 通过 `allowed-tools` 声明所需工具，命令文件进一步限制 |
| **人工闸门** | Git 写操作、高风险变更必须用户逐项确认（铁律#11） |
| **敏感信息脱敏** | HTML 报告和日志自动脱敏 Token/密钥/内部 URL（铁律#12） |
| **自定义步骤预确认** | 用户自定义 Skill 在执行前必须用户确认（铁律#13） |
| **文件写保护** | 所有写操作限定在项目根目录内（铁律#14） |
| **HITL 终极闸门** | 关键决策由人类拍板，Agent 是建议者而非决策者 |
| **供应链检查** | 新增依赖自动检查许可证兼容性和已知漏洞 |
| **递归保护** | Hook 脚本内置递归检测，防止 Agent 触发的 Hook 再次触发 Agent |

完整安全设计详见 `skills/fullchain-dev-workflow/references/security-policy.md`。

## 已知限制

| 限制 | 影响 | 缓解措施 |
|------|------|---------|
| MCP Server 自动启用 | `enableAllProjectMcpServers: true` 自动加载所有 MCP | 仅添加可信 MCP Server；审查 `.mcp.json` 内容 |
| Bash 权限粒度 | 命令文件的 `allowed-tools: Bash` 未限制具体命令 | `settings.local.json` 中通过 allowlist 限制 |
| 知识库 SQLite | 对话内容存储在本地 SQLite 文件 | `knowledge/conversation.db` 已加入 `.gitignore` |
| Excalidraw HTTP | 本地画布使用 HTTP（非 HTTPS） | 仅 loopback（127.0.0.1），不暴露到网络 |

## 安全检查清单

如果你在部署或二次开发 EasyWork，请确认：

- [ ] `.mcp.json` 中仅包含可信的 MCP Server
- [ ] `.easywork/config.json` 中的 `risk.high_risk_patterns` 覆盖你的业务场景
- [ ] `settings.local.json` 中的 Bash allowlist 已根据你的环境收紧
- [ ] Hook 脚本未被人篡改
- [ ] `knowledge/` 目录的访问权限已限制（如包含敏感对话记录）
- [ ] 自定义 Skill 的 `allowed-tools` 遵循最小权限原则
- [ ] 未在 Skill 文件或配置中硬编码凭据

## 致谢

感谢以下安全研究人员对 EasyWork 的帮助（按时间排序）：

（暂无）
