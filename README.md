# 身份证号码生成与校验工具 (guessID)

一个高效、准确的中国大陆居民身份证号码生成、校验与筛选工具。支持通配符匹配、实时性别筛选，并自动使用最新行政区划代码。

---

## 项目特点

- **智能通配符支持**：使用 `*` 替代未知数字，可灵活匹配部分已知信息的身份证号码
- **最新行政区划数据**：优先从 GitHub 获取最新 `areas.json`，网络失败时自动使用本地备用文件
- **性别精准筛选**：支持仅男性、仅女性或全部结果
- **高性能多线程**：默认 12 线程，可根据 CPU 调整
- **实时内存监控**：防止大范围搜索时内存占用过高
- **严格校验算法**：完整实现身份证校验码（第18位）验证
- **友好输出**：显示城市名称、生成估算数量、运行耗时等信息

---

## 安装依赖

### 1. 克隆或下载项目

``` BASH
git clone https://github.com/T0w3rH/GuessID.git
cd GuessID
````

### 2. 安装依赖库

``` BASH
# 推荐使用国内镜像加速
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

或手动安装：

``` BASH
pip install requests psutil
```

### 3. 准备本地备用数据（可选但推荐）

``` BASH
# 下载命令（Linux/macOS）
curl -o areas.json https://raw.githubusercontent.com/modood/Administrative-divisions-of-China/master/dist/areas.json
```

---

## 使用方法

``` BASH
python3 guessID.py
```

### 使用示例

输入格式示例：

- 12345612345678****

---

## 项目文件结构

``` TEXT
GuessID/
├── guessID.py              # 主程序（核心）
├── areas.json              # 本地行政区划数据（备用）
├── requirements.txt        # 依赖列表
├── README.md               # 本说明文件
└── resultID.txt            # 运行后自动生成的结果文件（追加模式）
```

---

## 依赖库

- **requests**：用于获取最新城市代码
- **psutil**：实时内存监控
- **Python 3.6+**：推荐使用 Python 3.8 或更高版本

---

## 鸣谢

本项目分别参考了 [**cnIDNumberGuesser**](https://github.com/Gloridust/cnIDNumberGuesser) 和 [**Administrative-divisions-of-China**](https://github.com/modood/Administrative-divisions-of-China) 的内容。十分感谢两位作者的开源贡献！

---

## 注意事项

- **合法用途**：本工具仅供学习、测试及个人研究使用，请遵守相关法律法规
- **大规模搜索**：当通配符较多时，候选数量会极大增加，请谨慎使用
- **网络依赖**：首次运行建议保持网络连接以获取最新行政区划代码
- **性能建议**：CPU 核心数越多，thread_count 可适当调高（推荐 8~16）

---

## License

MIT License © 2026

**仅供学习交流使用，请勿用于非法用途。**