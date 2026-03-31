## ✨ 新功能
- **core**: 新增 `RateLimitHook` 滑动窗口限流，支持 user/group/global 等多粒度 key，附带 `rate_limit()` 便捷工厂 (c570120d)
- **adapter**: NapCat 内置插件开关（`enable_napcat_builtin_plugins`）与配置流程优化 (e82ad3b5)

## 📝 文档
- 补充 `RateLimitHook` 参考文档与示例
- 补充 `napcat_comment` 工厂函数与 NapCat comment 格式说明

## ✅ 测试
- 新增 K-23: RateLimitHook 窗口滑动、超限、多粒度 key 等场景覆盖 (c570120d)
- 新增 S-08/S-09: NapCat 配置安全策略与插件开关测试 (e82ad3b5)
