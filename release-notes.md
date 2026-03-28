## ✨ 新功能
- **cli**: `ncatbot run` 新增 `--non-interactive`、`--bot-uin`、`--root` 参数；bot_uin 为默认值时自动进入 `ncatbot init` 初始化流程 (22b3139)
- **scripts**: 新增架构检查和运行时导入检查脚本 (511d87e)

## 🐛 修复
- **utils**: `confirm`/`async_confirm` 中断（Ctrl+C / EOF）时始终返回 `False` 而非 `default`，避免 `default=True` 场景下误同意；分离 `KeyboardInterrupt`/`EOFError` 处理并添加日志 (6208225)

## ♻️ 重构
- **imports**: 清理运行时导入，迁移 `pip_helper` 到 `utils`，移除 `requests` 依赖 (7e70665)

## 📝 文档
- 更新 CLI 命令参考、配置参考、环境变量汇总，补充 `NCATBOT_NON_INTERACTIVE`、`NCATBOT_BOT_UIN`、`NCATBOT_ROOT` 等环境变量说明

## 🔧 维护
- **skills**: 补充导入规范 Rule 5，同步 code-nav、docs-maintenance、testing-framework 知识资产 (bf7bda9, f1e49da)
