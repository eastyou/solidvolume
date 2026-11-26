# solidvolume

[![CI](https://github.com/eastyou/solidvolume/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/solidvolume/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](pyproject.toml)

一个面向初中数学课堂的立体图形体积与表面积计算工具，同时可以生成 A4 练习纸与演示页。

覆盖长方体、正方体、圆柱、圆锥、球五种常见立体，所有体积按立方单位、表面积按平方单位输出并保留 2 位小数；全部使用 Python 标准库，零第三方依赖。

## 特性

- 五种立体一键计算：`box`、`cube`、`cylinder`、`cone`、`sphere` 各对应一个子命令。
- 每条结果都会附上所用公式与代入的尺寸，方便课堂上对照讲解。
- 圆柱表面积包含两个底面，圆锥表面积包含底面且母线用勾股定理计算。
- 一条命令生成 A4 打印版练习纸，`--answers` 可附加答案与解题过程。
- `demo` 子命令手写 SVG 绘制五种立体的简图，并附公式卡片与例题。
- 相同 `--seed` 生成的练习纸完全一致，方便批改与重复印发。
- 所有外部输入都会校验：布尔值、空值、非数字、NaN、无穷大与越界值都会被拒绝。
- 全部函数带类型注解，兼容 Python 3.9 及以上版本。

## 安装

```bash
pip install .
```

安装后可直接使用 `solidvolume` 命令，也可以 `python -m solidvolume` 运行。

## 使用

```bash
$ solidvolume --help
usage: solidvolume [-h] [--version] 子命令 ...

初中数学：立体图形的体积与表面积计算工具。

positional arguments:
  子命令
    box       计算长方体的体积与表面积
    cube      计算正方体的体积与表面积
    cylinder  计算圆柱的体积与表面积
    cone      计算圆锥的体积与表面积
    sphere    计算球的体积与表面积
    sheet     生成 A4 练习纸
    demo      生成演示页

options:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
```

```bash
$ solidvolume box --length 3 --width 4 --height 5
长方体体积：60.00 立方单位
长方体表面积：94.00 平方单位
依据：V = 长×宽×高，S = 2×(长×宽+长×高+宽×高)，长 3、宽 4、高 5

$ solidvolume cube --edge 3
正方体体积：27.00 立方单位
正方体表面积：54.00 平方单位
依据：V = 棱长³，S = 6×棱长²，棱长 3

$ solidvolume cylinder --radius 2 --height 5
圆柱体积：62.83 立方单位
圆柱表面积：87.96 平方单位
依据：V = πr²h，S = 2πr²+2πrh，半径 2、高 5

$ solidvolume cone --radius 2 --height 6
圆锥体积：25.13 立方单位
圆锥表面积：52.30 平方单位
依据：V = πr²h÷3，S = πr²+πrl，母线 l = √(r²+h²) ≈ 6.32，半径 2、高 6

$ solidvolume sphere --radius 3
球体积：113.10 立方单位
球表面积：113.10 平方单位
依据：V = 4πr³÷3，S = 4πr²，半径 3

$ solidvolume sheet --count 8 --seed 1 -o sheet.html
已生成练习纸：sheet.html
题目数：8，答案：不含

$ solidvolume sheet --count 4 --seed 2 --answers -o answers.html
已生成练习纸：answers.html
题目数：4，答案：含

$ solidvolume demo -o demo.html
已生成演示页：demo.html
```

输入非法时，错误信息写入标准错误并返回退出码 2：

```bash
$ solidvolume cube --edge abc
错误：棱长 必须是数字，收到 'abc'
$ echo $?
2
```

### 参数

| 子命令 | 参数 | 说明 | 取值范围 |
| --- | --- | --- | --- |
| `box` | `--length` | 长 | 大于 0 且不超过 1000000 |
| `box` | `--width` | 宽 | 大于 0 且不超过 1000000 |
| `box` | `--height` | 高 | 大于 0 且不超过 1000000 |
| `cube` | `--edge` | 棱长 | 大于 0 且不超过 1000000 |
| `cylinder` | `--radius` | 底面半径 | 大于 0 且不超过 1000000 |
| `cylinder` | `--height` | 高 | 大于 0 且不超过 1000000 |
| `cone` | `--radius` | 底面半径 | 大于 0 且不超过 1000000 |
| `cone` | `--height` | 高 | 大于 0 且不超过 1000000 |
| `sphere` | `--radius` | 半径 | 大于 0 且不超过 1000000 |
| `sheet` | `--count` | 练习题数量 | 1 到 50，默认 8 |
| `sheet` | `--seed` | 随机种子 | 任意整数，默认 1 |
| `sheet` | `-o, --output` | 输出 HTML 文件路径 | 必填 |
| `sheet` | `--answers` | 是否附答案与解题过程 | 开关项 |
| `demo` | `-o, --output` | 输出 HTML 文件路径 | 必填 |

计算结果必须是有限值且小于 10^15，超出时按输入非法处理。

### 退出码

| 退出码 | 含义 |
| --- | --- |
| 0 | 计算成功或文件生成成功 |
| 2 | 参数缺失、输入非法、越界或写入文件失败 |

## 作为库使用

```python
from solidvolume import (
    box_surface,
    box_volume,
    cone_surface,
    cone_volume,
    make_questions,
    render_sheet,
    sphere_surface,
    sphere_volume,
)

print(round(box_volume(3, 4, 5), 2))      # 60.0
print(round(box_surface(3, 4, 5), 2))     # 94.0
print(round(cone_volume(2, 6), 2))        # 25.13
print(round(cone_surface(2, 6), 2))       # 52.3
print(round(sphere_volume(3), 2))         # 113.1

questions = make_questions(count=8, seed=1)
html_text = render_sheet(questions, answers=True)
print(len(questions))                     # 8
```

## 开发与测试

```bash
python -m unittest discover -s tests -v
```

共 124 个测试用例，覆盖五种立体的正常值与公式关系、边界值（边长为 0、负数、超过 10^6、结果溢出）、非法输入的错误码与错误信息、HTML/SVG 可被 `html.parser` 解析、种子可复现以及每个子命令。

## License

[MIT](LICENSE) © 2026 eastyou
