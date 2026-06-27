# Debug Module

## 目标

Debug 模块负责统一管理 MatterCraft 的调试信息输出、日志分级、模块来源标记和 debug 窗口布局。项目中不得绕过 Debug 模块直接输出调试信息。

## 基础规范

1. 所有调试信息必须使用 `debug.log` 输出。
2. 每条日志必须明确日志等级。
3. 每条日志必须明确来源模块。
4. 日志内容需要清晰说明事件、状态或异常上下文。
5. Debug 模块负责统一管理日志展示方式，业务模块只负责提交日志内容。

推荐调用形式：

```python
debug.log(level="info", module="logic", message="Player movement updated.")
```

## 日志等级

推荐日志等级：

- `debug`：细粒度调试信息，仅用于开发过程中的状态观察。
- `info`：普通运行信息，用于描述重要但正常的状态变化。
- `warning`：潜在问题，程序仍可继续运行。
- `error`：明确错误，当前操作失败或需要开发者介入。

## 模块标记

日志必须带有模块来源，推荐使用项目核心结构作为一级模块名：

- `descriptor`
- `calculus`
- `logic`
- `debug`
- `render`
- `input`
- `pygame`

当模块需要更细分时，可以使用点号连接，例如：

```python
debug.log(level="debug", module="logic.player", message="Jump request accepted.")
```

## 启动方式

运行项目时，可以通过命令行添加 `debug` 参数开启 debug 模式。

预期行为：

1. 正常打开游戏主窗口。
2. 同时打开一个 debug 窗口。
3. debug 窗口由 Debug 模块统一管理布局和内容更新。

示例：

```bash
python main.py debug
```

## Debug 窗口职责

Debug 窗口用于清晰展示调试信息，布局由 Debug 模块统一管理。

建议展示区域：

- 日志列表：按时间顺序展示日志。
- 等级筛选：按 `debug`、`info`、`warning`、`error` 过滤。
- 模块筛选：按模块来源过滤。
- 运行状态：展示 FPS、当前场景、对象数量等运行时状态。
- 错误区域：突出展示 `error` 等级日志。

## 实现要求

Debug 模块实现时需要遵守：

1. Debug 模式关闭时，`debug.log` 仍然可以被调用，但不应打开 debug 窗口。
2. Debug 模式开启时，主窗口和 debug 窗口需要同时存在。
3. Debug 窗口的布局、刷新、筛选和渲染逻辑集中在 Debug 模块内部。
4. 其他模块不得直接操作 debug 窗口布局。
5. 与 Debug 模块相关的 class 和函数必须包含功能、参数信息和实现逻辑注释。

## 与项目结构的关系

Debug 模块可以服务于 `descriptor`、`calculus` 和 `logic`，但不应侵入这些模块的核心逻辑。

推荐边界：

- 业务模块调用 `debug.log` 提交事件。
- Debug 模块收集、存储、过滤和展示事件。
- Debug 窗口只展示调试状态，不改变游戏主逻辑。

