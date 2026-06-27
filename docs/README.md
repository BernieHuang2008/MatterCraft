# MatterCraft Docs

## 文档导航

MatterCraft 采用文档优先的开发方式。所有代码修改前，需要先阅读本目录下与修改内容相关的文档，并在实现时遵守对应规范。

当前文档结构：

- `dev_note/README.md`：开发概念与项目代码规范总览。
- `dev_note/code_standard.md`：命名、注释、类型注解、核心结构与实现记录规范。
- `matter_core/README.md`：MatterCraft 核心物质表示层的设计总览。
- `matter_core/ldc_structure.md`：LDC 三版本结构说明。
- `matter_core/object_identity_and_hash.md`：对象 `_id` 与 `hash()` 规则。
- `matter_core/units_and_precision.md`：全项目基础量单位与精度规范。
- `matter_core/core_classes/README.md`：Atom、Bond、Molecule、Matter、Mixture 的核心 class 设计导航。
- `matter_core/preset_database/atompresetdatabase.md`：AtomPresetDatabase 字段与 CSV 规范。
- `matter_core/todo.md`：核心物质表示层的待讨论问题。
- `debug_module/README.md`：Debug 模块专用规范与设计要求。

## 开发前检查

进行代码修改前，请按以下顺序确认：

1. 阅读本导航，确认修改涉及的文档范围。
2. 阅读 `dev_note/README.md`，确认项目核心结构和基础约束。
3. 若修改涉及核心物质表示、对象结构、反应推断基础数据，必须阅读 `matter_core/README.md`。
4. 若修改涉及日志、调试窗口或 debug 参数，必须阅读 `debug_module/README.md`。
5. 在对应函数或 class 的注释中写明实现逻辑，保持代码与文档同步。
