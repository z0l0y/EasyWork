# 语言与技术栈适配速查

本文档帮助 Agent 在不同语言/框架的项目中正确执行 EasyWork 各步骤的操作。
每个操作列出常见技术栈的具体命令、配置文件位置和注意事项。

## 测试命令速查

### 如何找到测试命令

| 语言/框架 | 搜索位置 | 典型命令 | 运行子集 |
|----------|---------|---------|---------|
| **Node.js / Jest** | `package.json` → `scripts.test` | `npm test` / `npx jest` | `npx jest --testPathPattern="auth"` |
| **Node.js / Mocha** | `package.json` → `scripts.test` | `npm test` / `npx mocha` | `npx mocha --grep "auth"` |
| **Node.js / Vitest** | `package.json` → `scripts.test` | `npm test` / `npx vitest` | `npx vitest -t "auth"` |
| **Python / pytest** | `pyproject.toml` / `setup.cfg` | `pytest` | `pytest tests/test_auth.py -k "login"` |
| **Python / unittest** | `Makefile` / CI config | `python -m unittest` | `python -m unittest tests.test_auth.TestLogin` |
| **Go** | `Makefile` / CI config | `go test ./...` | `go test ./... -run TestLogin` |
| **Java / Maven** | `pom.xml` | `mvn test` | `mvn test -Dtest=AuthServiceTest` |
| **Java / Gradle** | `build.gradle` | `./gradlew test` | `./gradlew test --tests "AuthServiceTest"` |
| **Rust** | `Cargo.toml` | `cargo test` | `cargo test auth::` |
| **Ruby / RSpec** | `Gemfile` | `bundle exec rspec` | `bundle exec rspec spec/auth/` |
| **PHP / PHPUnit** | `composer.json` | `./vendor/bin/phpunit` | `./vendor/bin/phpunit --filter=AuthTest` |
| **C# / .NET** | `*.csproj` | `dotnet test` | `dotnet test --filter "FullyQualifiedName~Auth"` |

### 无测试框架时的最小补充

| 语言 | 推荐的测试框架 | 安装命令 |
|------|-------------|---------|
| Node.js | Jest（零配置） | `npm install --save-dev jest` |
| Python | pytest | `pip install pytest` |
| Go | testing（内置） | 无需安装 |
| Java | JUnit 5 | Maven/Gradle 添加依赖 |
| Rust | `#[test]`（内置） | 无需安装 |

---

## 代码风格检查速查

### 如何找到项目的风格配置

| 语言 | 搜索的配置文件 | 常见工具 |
|------|-------------|---------|
| **JavaScript/TypeScript** | `.eslintrc.*` / `eslint.config.*` / `.prettierrc*` | ESLint, Prettier |
| **Python** | `pyproject.toml` → `[tool.ruff]` / `[tool.black]` / `.flake8` | Ruff, Black, Flake8, mypy |
| **Go** | `go.mod` → Go version | `gofmt`（内置）, `golangci-lint` |
| **Java** | `checkstyle.xml` / `pom.xml` → checkstyle plugin | Checkstyle, SpotBugs |
| **Rust** | `rustfmt.toml` / `.rustfmt.toml` | `rustfmt`（内置）, `clippy` |
| **Ruby** | `.rubocop.yml` | RuboCop |
| **PHP** | `phpcs.xml` / `.php-cs-fixer.php` | PHP_CodeSniffer, PHP-CS-Fixer |
| **C#** | `.editorconfig` / `Directory.Build.props` | StyleCop, dotnet-format |

### 如何提取项目风格特征

对所有语言通用的风格探测步骤：

1. **找到最近修改的源文件**：
   ```bash
   git log --oneline -5 --name-only
   ```
   查看那些被人为修改的文件（而非自动生成的文件）

2. **提取关键风格特征**：
   - 缩进：空格还是 Tab？几个空格？
   - 引号：单引号还是双引号？
   - 分号：使用还是省略？
   - 命名风格：camelCase / snake_case / PascalCase / kebab-case？
   - 文件命名：风格一致还是随意的？
   - 导入分组：按什么逻辑分组（第三方/内部/相对）？

3. **找到同类型文件**：
   - 如果要新增一个 Service，先看项目现有 Service 的写法
   - 如果要新增一个 API 端点，先看项目现有路由的写法

---

## 包管理/依赖速查

| 语言 | 包管理文件 | 安装依赖 | 查看依赖树 |
|------|----------|---------|----------|
| Node.js | `package.json` | `npm install` / `yarn` / `pnpm install` | `npm ls` |
| Python | `pyproject.toml` / `requirements.txt` | `pip install -r requirements.txt` | `pip list` |
| Go | `go.mod` | `go mod download` | `go mod graph` |
| Java (Maven) | `pom.xml` | `mvn install` | `mvn dependency:tree` |
| Java (Gradle) | `build.gradle` | `./gradlew build` | `./gradlew dependencies` |
| Rust | `Cargo.toml` | `cargo build` | `cargo tree` |
| Ruby | `Gemfile` | `bundle install` | `bundle list` |
| PHP | `composer.json` | `composer install` | `composer show` |

---

## 构建/编译速查

| 语言 | 构建配置 | 构建命令 | 产物目录 |
|------|---------|---------|---------|
| TypeScript | `tsconfig.json` | `npx tsc` / `npm run build` | `dist/` / `build/` |
| Python | — | 无需编译（解释型） | — |
| Go | `go.mod` | `go build ./...` | 可执行文件 |
| Java (Maven) | `pom.xml` | `mvn compile` / `mvn package` | `target/` |
| Java (Gradle) | `build.gradle` | `./gradlew build` | `build/` |
| Rust | `Cargo.toml` | `cargo build` / `cargo build --release` | `target/debug/` / `target/release/` |

---

## CI/CD 配置速查

| CI 平台 | 配置文件位置 |
|---------|-----------|
| GitHub Actions | `.github/workflows/*.yml` |
| GitLab CI | `.gitlab-ci.yml` |
| Jenkins | `Jenkinsfile` |
| CircleCI | `.circleci/config.yml` |
| Travis CI | `.travis.yml` |
| Bitbucket Pipelines | `bitbucket-pipelines.yml` |
| 阿里云 云效 | `.aliyun/pipeline.yml` |
| 腾讯云 CODING | `.coding-ci.yml` |

---

## 语言特有的审查要点

### Node.js / TypeScript
- `package.json` 中是否新增了依赖？版本号是否锁定？
- TypeScript 项目：是否使用了 `any` 类型规避检查？
- 是否滥用 `as` 类型断言？
- Promise 是否都做了 reject 处理？
- 事件监听器是否在适当时机移除？

### Python
- 是否使用了 `except Exception` 的裸捕获？
- 是否有循环内执行 SQL 查询？
- 是否使用了可变默认参数（`def fn(x=[])`）？
- 文件操作是否使用了 `with` 上下文管理器？
- 是否引入了不必要的重依赖（如仅为了一个函数引入 pandas）？

### Go
- error 是否都被检查了（不能忽略 `_`）？
- defer 的使用顺序是否正确？
- goroutine 是否有泄漏风险（是否有退出机制）？
- 是否在循环内拼接字符串（应用 `strings.Builder`）？
- 公共 API 是否有 godoc 注释？

### Java
- 资源是否在 try-with-resources 中正确关闭？
- 是否有 SQL 注入风险（拼接 SQL 字符串）？
- 是否有线程安全问题（共享可变状态未同步）？
- Entity 的 equals/hashCode 是否同时重写？
- 依赖注入是否正确（而非 new 创建 Service）？

### Rust
- 是否滥用 `unwrap()` / `expect()`？
- 是否有不必要的 `.clone()` 调用？
- 借用检查器是否被 `unsafe` 绕过？
- 是否遵循了项目中现有的错误处理模式（anyhow / thiserror）？

---

## READ 阶段多语言适配

| 语言 | 如何搜索模块依赖关系 | 如何找到所有调用方 |
|------|-------------------|------------------|
| TypeScript/JS | `grep -r "import.*from.*moduleName" src/` | `grep -r "functionName\|ClassName" src/` |
| Python | `grep -r "from module import\|import module" .` | `grep -r "def function_name\|class ClassName" .` |
| Go | `grep -r "packageName\." .` | `grep -r "FunctionName(" .` |
| Java | IDE: Find Usages | `grep -r "ClassName\|methodName" src/` |
| Rust | `grep -r "use crate::module\|use mod_name" src/` | `grep -r "fn_name\|StructName" src/` |
