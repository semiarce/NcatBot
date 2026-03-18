# 测试规范编号

框架测试使用规范编号标识每个测试用例，格式为 `前缀-序号`。

## 编号表

| 前缀 | 模块 | 范围 | 测试文件位置 |
|------|------|------|-------------|
| T | Types / Segments | T-01 ~ T-14 | `tests/unit/types/` |
| S (types) | Segment 解析 (parse_segment) | S-01 ~ S-10 | `tests/unit/types/` |
| CQ | CQ 码解析 | CQ-01 ~ CQ-08 | `tests/unit/types/` |
| E | Event Entity / Factory | E-01 ~ E-07 | `tests/unit/event/` |
| A | API Client | A-01 ~ A-05 | `tests/unit/api/` |
| P | EventParser / NapCatEventParser | P-01 ~ P-07 | `tests/unit/adapter/` |
| RD | 真实数据驱动解析 | RD-01 ~ RD-03 | `tests/unit/adapter/` |
| AR | AdapterRegistry | AR-01 ~ AR-05 | `tests/unit/adapter/` |
| CF | Config Migration | CF-01 ~ CF-06 | `tests/unit/config/` |
| D | AsyncEventDispatcher | D-01 ~ D-09 | `tests/unit/core/` |
| K | Hook System | K-01 ~ K-07 | `tests/unit/core/` |
| H | HandlerDispatcher | H-01 ~ H-12 | `tests/unit/core/` |
| R | Registrar | R-01 ~ R-06 | `tests/unit/core/` |
| R (plugin) | Registrar × ModuleImporter 去重 | R-10 ~ R-11 | `tests/unit/plugin/` |
| S (svc) | ServiceManager | S-01 ~ S-08 | `tests/unit/service/` |
| M | Plugin Mixin | M-01 ~ M-41 | `tests/unit/plugin/` |
| I | Integration | I-01 ~ I-21 | `tests/integration/` |
| B | BotClient E2E | B-01 ~ B-05 | `tests/e2e/` |
| NC | NapCat E2E | NC-01 ~ NC-21 | `tests/e2e/napcat/` |
| PL | Plugin E2E | PL-01 ~ PL-53 | `tests/e2e/plugin/` |

## 命名规范

测试函数的 docstring 第一行包含规范编号：

```python
async def test_dispatcher_routes_group_message(event_dispatcher):
    """D-03: AsyncEventDispatcher 正确路由群消息到 message.group 订阅者"""
    ...
```

## 新增测试编号

在对应前缀的最大序号上 +1。例如现有 D-01 ~ D-09，新增时使用 D-10。

## 已分配编号记录

| 前缀 | 当前最大序号 | 最后更新 |
|------|-------------|--------|
| R | R-09 | 2026-03-16：R-07~R-09 堆叠装饰器去重 |
| R | R-11 | 2026-03-17：R-10~R-11 __init__.py 双重 exec 去重 |
| AR | AR-05 | AdapterRegistry register/discover/create/list/error |
| CF | CF-06 | Config migration: legacy→new, defaults, coerce, to_dict |
| PL | PL-53 | Plugin E2E: hello_world/event_handling/hook_filter/dialog/full |
