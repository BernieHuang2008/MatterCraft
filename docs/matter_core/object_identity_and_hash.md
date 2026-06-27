# Object Identity And Hash

## `_id`

所有核心 object 默认拥有 `_id` 字段。

`_id` 表示 object instance 的唯一 id，由全局 ID 分发器统一生成。

示例：

```text
ATOM_000001
BOND_000001
MOL_000001
MAT_000001
MINT_000001
MIXT_000001
MIXC_000001
```

规则：

1. `_id` 是系统字段，不使用 `b` 或 `a` 前缀。
2. id 前缀必须全大写。
3. 不同 class 使用不同 id 前缀。
4. `_id` 只用于区分实例，不用于判断对象性质是否相同。
5. `_id` 不参与 `hash()` 计算。

## Global Id Dispatcher

全局 ID 分发器负责为不同 class 分配唯一 id。

推荐职责：

1. 管理 class name 与 id prefix 的映射关系。
2. 为每个 id prefix 维护独立计数器。
3. 生成形如 `PREFIX_000001` 的稳定格式。
4. 避免不同 class 或不同模块之间手动生成重复 id。

## `hash()`

每个核心 class 都需要实现自己的：

```python
def hash(self) -> str:
```

`hash()` 无参数，作用是实时计算当前 object 的性质哈希。

规则：

1. 最后一步使用 SHA-256。
2. `hash()` 判断对象性质是否完全相同，而不是判断是否为同一个 instance。
3. 同一个对象的 `Logic`、`Descriptor` 和 `Calculus` 三个版本必须拥有相同的 hash。
4. 若两个 object 的参与哈希属性完全相同，则它们的 `hash()` 结果应该相同。
5. 若两个 object 的参与哈希属性不同，则它们的 `hash()` 结果应该不同。
6. `_id` 不参与哈希。
7. `r` 前缀的 runtime reference 不参与哈希。
8. `a` 前缀的 auto calculated property 默认不参与哈希，因为它们应该由 `b` 属性推出。
9. 缓存、窗口状态、临时计算结构和运行时 debug 信息不参与哈希。
10. 不使用 Python 内置 `hash()` 作为最终哈希值，因为它不适合跨运行稳定比较。

## `b` Property Rule

`b` 表示 `basic property that uniquely defines an object`。因此，descriptor 中所有以 `b` 开头的属性都必须进入 hash。

特殊说明：

1. `hash()` 只扫描 descriptor 中的 `b` 属性。
2. `Logic` 或 `Calculus` 中的 runtime reference 不因为命名或引用关系进入 hash。
3. parent object reference 这类字段应该使用 `r` 前缀，例如 `rParentMolecule`，不应使用 `b` 前缀。
4. 如果某个字段不应该进入 hash，它就不应该以 `b` 开头，也不应该存在于 descriptor 的 basic property 集合中。

## 推荐哈希流程

推荐使用以下流程：

```text
convert to descriptor -> collect b properties -> canonical payload -> canonical JSON -> SHA-256
```

具体步骤：

1. 如果当前对象是 `Logic` 或 `Calculus`，先调用 `toDescriptor()`。
2. 从 descriptor 中收集所有以 `b` 开头的属性。
3. 构造 canonical payload：

```python
{
    "hashSchemaVersion": 1,
    "objectType": "Atom",
    "bProperties": {
        "bAtomicNumber": 8,
        "bMassNumber": 16,
        "bCharge": 0,
        "bElectronConfig": {
            "1s": [2],
            "2s": [2],
            "2p": [2, 1, 1],
        },
    },
}
```

4. `hashSchemaVersion` 用于未来升级哈希规则。
5. `objectType` 用于区分不同 class，避免不同类型对象因为字段值偶然相同而得到相同 hash。
6. 对 `dict` 和 object property 按键名的 ASCII 升序排列。
7. 对有序 `list` 保留原顺序，例如 `bElectronConfig` 中同一能级的轨道占据列表。
8. 对 `set` 或无序对象集合，先计算每个子对象的 hash，再转换为 list，并按 hash 的 ASCII 升序排列。
9. 如果无序集合中存在性质相同的重复对象，需要保留重复项。例如 H-H 键的 `bAtomList` 规范化后可以是 `[H_atom_hash, H_atom_hash]`。
10. 子对象不使用 `_id` 参与哈希，而是使用子对象自己的 `hash()`。
11. 将 canonical payload 序列化为 canonical JSON。
12. 对 canonical JSON 的 UTF-8 bytes 计算 SHA-256。
13. 返回 SHA-256 的 lowercase hex digest。

推荐 canonical JSON 设置：

```text
sort_keys = True
ensure_ascii = False
separators = (",", ":")
```

浮点数规则：

1. 进入 hash 前必须先转换到 `units_and_precision.md` 规定的标准单位。
2. 浮点数应转换为稳定 decimal string，避免二进制浮点误差直接进入 JSON。
3. 每个字段的具体精度以 `units_and_precision.md` 为准。

## MixtureComponent Canonical Rule

`MixtureComponent` 中与宏观组织有关的字段使用以下 canonical 规则：

1. `bSpatialDistribution` 必须是枚举字符串，只允许 `homogeneous`、`layered`、`suspended`、`granularRandom`、`phaseSeparated`。
2. `bContactRelation` 必须使用固定 schema：

```python
{
    "model": "pairwise",
    "relationList": [
        {
            "targetComponentHash": "<sha256>",
            "relationType": "interface",
            "contactArea": "1.200000000000e-06",
            "contactAreaUnit": "m^2"
        }
    ]
}
```

3. `relationList` 进入 hash 前按 `targetComponentHash` 和 `relationType` 的 ASCII 升序排序。
4. `contactArea` 使用 decimal string，并在进入 hash 前规范到标准单位 `m^2`。

## 子对象参与规则

当 object 包含其他 object 时，不应该直接把子对象的内存地址放入哈希。

推荐规则：

- `Atom`：使用自身基础属性参与哈希。
- `Bond`：使用参与键的 Atom hash、键类型、键级、电子数、是否离域等属性参与哈希。
- `Molecule`：使用 Atom hash 集合和 Bond hash 集合参与哈希。
- `Matter`：使用 Molecule hash 集合和物理组织属性参与哈希。
- `Mixture`：使用 MixtureComponent hash 集合参与哈希。
