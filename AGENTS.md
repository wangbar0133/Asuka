# AGENTS.md — Asuka 仓库协作说明

本文件面向在此仓库工作的 AI agent 与人类开发者。做任何事之前先读完本文件。

## 项目简介

Asuka 是一个基于 Python 3.11+ 和 ANTLR4 的 Solidity 智能合约缺陷检测器。
输入可以是本地文件/目录,也可以是链上合约地址(经 Etherscan 拉取源码)。
检测结果按 SWC 编号分类,按风险等级输出。

## 环境搭建

```bash
python3.11 -m venv .venv          # 需要 Python >= 3.11
.venv/bin/pip install -e ".[dev]"
```

一条命令完成可编辑安装 + 测试/lint 工具。日常所有命令都通过 `.venv/bin/...` 执行。

## 常用命令

| 用途 | 命令 |
|---|---|
| 测试 | `.venv/bin/pytest` |
| Lint | `.venv/bin/ruff check .` |
| Lint 自动修复 | `.venv/bin/ruff check --fix .` |
| CLI 扫描 | `.venv/bin/asuka .` 或 `.venv/bin/python -m core .` |
| 单文件扫描 | `.venv/bin/asuka test_data/reentrancy.sol` |
| 指定检测器 | `.venv/bin/asuka . -i s107,101` |
| 查看检测器列表 | `.venv/bin/asuka -d` |

**提交前必须 `pytest` 和 `ruff check .` 双绿。** CI(GitHub Actions)会在
Python 3.11–3.14 矩阵上强制执行同样检查。

## 架构

```
CLI 入口            core/__main__.py   argparse;core/asuka.py  Asuka 类,multiprocessing.Pool 并发
   │
   ├─ 远程地址      scraper/scraper.py Etherscan API 拉源码到 /tmp/AsukaTmp
   │
   ├─ 解析          solidity_antlr4_parser/  ANTLR 生成的词法/语法分析 + parser.py(objectify)
   │
   ├─ AST 扫描      ast_scanner/ast_scanner.py  Scanner/Contract/Function 三层,提取语句/表达式/函数调用
   │
   ├─ 检测器        vuls/*.py  每个文件一个 SWC 检测器,全部在 vuls/all_detector.py 注册
   │
   └─ 输出          core/printer.py  风险分级 + 源码片段定位
```

数据流:`.sol 文件 → parse_file() → objectify() → Scanner → detector.check(scanner) → Vuls`,
`VulTable`(dict 子类)按 SWC id 聚合各文件结果。

## 关键约定

### 检测器插件协议

`vuls/` 下每个检测器模块暴露模块级常量 + 一个 `check(scan: Scanner) -> Vuls` 函数:

- `NAME` / `ID`(SWC 编号)/ `DESCREIBE` / `ADVICE` / `RISK`(0=Info, 1=Low, 2=Medium, 3=High)
- 新检测器必须在 `vuls/all_detector.py` 追加导入(该文件靠 import 副作用注册,有 `# noqa: F401`,勿删)
- 模板见 `vuls/templates.py` 和 `vuls/README.md`

注意:`DESCREIBE`/`METHED` 是历史拼写错误,为保持公开接口兼容暂不改名,
优化路线里有统一重命名一项。

### 测试即行为基线

`tests/test_detectors.py` 的 `EXPECTED` 字典记录了 10 个测试合约 × 9 个检测器的
**精确发现数**。改变检测器逻辑时必须在同一提交里更新对应期望值,并说明原因。
新增检测器时同步更新 `EXPECTED_IDS` 和 `EXPECTED`。

### 版本号

唯一来源是 `core/__init__.py` 的 `__version__`,pyproject.toml 通过
`[tool.setuptools.dynamic]` 读取,banner 和 `--version` 都引用它。发版只改一处。

## 禁止事项

- **不要手改 `solidity_antlr4_parser/Solidity{Lexer,Parser,Listener,Visitor}.py`**:
  这些是 ANTLR 4.7.2 生成的代码(已从 ruff 排除)。唯一的例外是极小的兼容性补丁
  (如历史上 `typing.io` → `typing` 的修复),须单独提交并说明。
  `solidity_antlr4_parser/parser.py` 是手写的 objectify 层,可以正常修改。
- 不要提交 `debug.log`(CLI 运行时在 CWD 生成)、`.venv/`、`__pycache__/`。
- 不要在代码或测试里硬编码 API key(历史上有一个 Etherscan key 泄漏在 test.py,
  2023 年起已随迁移移除;新增网络测试一律 mock)。
- 不要在 import 时产生副作用(写文件、配置 logging)。logging 配置在
  `core/__main__.py:main()` 里,模块级只做声明。

## 已知坑

- `multiprocessing.Pool` 在 macOS 用 spawn 启动子进程,`Asuka` 实例会被 pickle,
  实例属性必须保持可 pickle。
- `scan_file` 里任何一个文件解析失败都会 `raise RuntimeError` 使整个扫描中止
  (优化路线里计划改为跳过并汇总报告)。
- `vuls/utils.py:check_solc_version` 只处理单版本 pragma,不支持 `||` 多段声明。
- ANTLR 运行时钉死在 `antlr4-python3-runtime==4.9.2`,升级需要重新生成 parser(见优化路线)。
