# Code Standard

## 命名规范

1. 所有类、类变量和方法都采用驼峰命名方式。
2. 类名首字母大写。
3. 所有类变量都需要添加语义前缀。

变量前缀约定：

- `b`：表示 `basic property that uniquely defines an object`，即唯一定义对象的基础属性。
- `a`：表示 `auto calculated property`，即自动计算属性。这类变量没有 setter，会自动与 getter 绑定，并通过延迟计算获得结果。
- `r`：表示 `runtime reference property`，即运行时引用属性。这类变量用于连接当前 object 与其他运行时 object，不属于 descriptor 中的真实物质属性，默认不参与 `hash()`。
- `etc.`：后续可根据项目需要扩展新的语义前缀，但必须先写入文档再进入实现。

示例：

```python
class MatterObject:
    bMass: float
    aVolume: float
    rParentObject: object
```

## 类型注解

所有函数都需要添加类型注解，包括：

- 参数类型。
- 返回值类型。
- 必要时的属性类型。

示例：

```python
def getMass(self) -> float:
    return self.bMass
```

## 注释规范

每个函数和 class 都必须有注释，至少注明：

1. 功能。
2. 参数信息。
3. 实现逻辑。

实现逻辑必须写在对应函数或 class 下方，方便后续从代码直接追踪设计意图。

推荐格式：

```python
class MatterObject:
    """
    功能：表示一个基础物质对象。
    参数：
        bMass: 对象质量，用于唯一描述对象的基础物理属性之一。
    实现逻辑：
        通过 descriptor 保存基础描述，通过 calculus 管理计算缓存，通过 logic 处理对象行为。
    """
```

```python
def calculateVolume(self) -> float:
    """
    功能：计算对象体积。
    参数：
        无。
    返回：
        float: 当前对象体积。
    实现逻辑：
        优先读取自动计算缓存；缓存不存在时根据对象 descriptor 中的基础属性重新计算。
    """
```

## 核心模块规范

每个 class 都需要在设计上对应以下三类结构：

- `descriptor`：保存对象描述符和基础定义。
- `calculus`：保存计算过程中的高效数据结构、缓存、索引或中间结果。
- `logic`：保存对象被操作时的行为接口和流程逻辑。

开发新对象时，需要先明确：

1. 哪些属性属于 `descriptor`。
2. 哪些属性属于 `calculus`。
3. 哪些操作属于 `logic`。

## 文档优先规则

所有代码修改必须遵守以下流程：

1. 先阅读 `docs/README.md` 的导航说明。
2. 根据修改内容阅读对应子文档。
3. 如果实现了新的规则、模块约定或 Debug 行为，需要先更新文档。
4. 代码中的函数和 class 注释必须和文档描述保持一致。

## Debug 输出规则

所有调试信息输出必须使用 `debug.log`。日志需要包含：

- 日志等级。
- 所属模块。
- 清晰的消息内容。

Debug 模块的详细规范见 `debug_module/README.md`。
