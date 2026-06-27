# LDC Structure

## 定义

`LDC` 是 MatterCraft 核心对象的三版本结构：

- `Logic`
- `Descriptor`
- `Calculus`

每个核心对象都需要按照这个结构组织，例如：

```text
AtomLogic
AtomDescriptor
AtomCalculus

MoleculeLogic
MoleculeDescriptor
MoleculeCalculus
```

## 三版本职责

| 版本 | 职责 |
| --- | --- |
| `Logic` | 代码逻辑清晰，是主要业务入口，可以不做极致优化 |
| `Descriptor` | 稳定描述对象，用于存档、构造、比对和文档化表达 |
| `Calculus` | 面向高性能计算，需要尽量减少不必要的自动计算和对象层级开销 |

## 转换规则

`Logic` 版本提供三版本之间的转换方法：

```text
toDescriptor()
fromDescriptor()
toCalculus()
fromCalculus()
```

实现要求：

1. 转换方法需要添加完整类型注解。
2. 转换方法需要在注释中说明功能、参数信息和实现逻辑。
3. `Descriptor` 应该优先保存稳定、可序列化的数据。
4. `Calculus` 可以保存为计算服务的压缩结构、索引结构或缓存结构。
5. `Logic` 负责保持对象操作语义清晰，并作为其他版本的转换中心。

## Hash Consistency

同一个对象的 `Logic`、`Descriptor` 和 `Calculus` 三个版本必须拥有相同的性质哈希。

示例：

```text
AtomLogic.hash() == AtomDescriptor.hash() == AtomCalculus.hash()
```

推荐实现方式：

1. `Descriptor.hash()` 直接根据 descriptor 中的 `b` 属性计算。
2. `Logic.hash()` 先调用 `toDescriptor()`，再复用 `Descriptor.hash()`。
3. `Calculus.hash()` 先调用 `toDescriptor()`，再复用 `Descriptor.hash()`。

这样可以保证三版本内部结构不同，但只要表达的是同一个物质对象，就会得到同一个 hash。
