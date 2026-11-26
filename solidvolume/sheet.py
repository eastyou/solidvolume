"""练习纸、演示页与题目生成。

HTML/SVG 全部用字符串拼接，文本一律经过 ``html.escape``，
不依赖第三方库，也不使用 xml.etree。
"""

import html
import math
import random
from typing import List, NamedTuple, Sequence, Tuple

from .core import (
    box_surface,
    box_volume,
    cone_slant_height,
    cone_surface,
    cone_volume,
    cube_surface,
    cube_volume,
    cylinder_surface,
    cylinder_volume,
    sphere_surface,
    sphere_volume,
)


class Question(NamedTuple):
    """一道练习题：题号、类型、题干、答案与解题过程。"""

    number: int
    kind: str
    prompt: str
    answer: str
    working: str


SHEET_CSS: str = """
@page { size: A4; margin: 16mm; }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 18mm 14mm; background: #f4f6f9;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif;
  color: #1f2933; line-height: 1.7;
}
.sheet {
  max-width: 760px; margin: 0 auto; padding: 28px 32px;
  background: #ffffff; border: 1px solid #d8dee9; border-radius: 10px;
}
header { border-bottom: 2px solid #1f2933; padding-bottom: 10px; margin-bottom: 18px; }
h1 { margin: 0 0 6px; font-size: 24px; letter-spacing: 1px; }
.meta { margin: 0; font-size: 13px; color: #52606d; }
ol.questions { margin: 0; padding-left: 24px; }
ol.questions > li { margin-bottom: 22px; page-break-inside: avoid; }
.prompt { margin: 0 0 8px; font-size: 15px; }
.blank { height: 46px; border-bottom: 1px dashed #9aa5b1; }
.answer { margin: 4px 0; font-size: 14px; color: #0b7285; }
.working { margin: 0; font-size: 13px; color: #52606d; }
.tips { margin-top: 22px; padding-top: 10px; border-top: 1px solid #d8dee9;
  font-size: 12px; color: #616e7c; }
@media print {
  body { background: #ffffff; padding: 0; }
  .sheet { border: none; border-radius: 0; max-width: none; padding: 0; }
}
"""

DEMO_CSS: str = """
body {
  margin: 0; padding: 32px 18px; background: #f4f6f9;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif;
  color: #1f2933; line-height: 1.7;
}
.wrap { max-width: 880px; margin: 0 auto; }
header { margin-bottom: 22px; }
h1 { margin: 0 0 5px; font-size: 26px; }
.sub { margin: 0; color: #52606d; font-size: 14px; }
.figures { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 14px; margin-bottom: 22px; }
figure { margin: 0; padding: 12px; background: #ffffff;
  border: 1px solid #d8dee9; border-radius: 10px; }
figure svg { width: 100%; height: auto; display: block; }
figcaption { margin-top: 6px; font-size: 13px; color: #52606d; text-align: center; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; }
.card { padding: 16px 18px; background: #ffffff; border: 1px solid #d8dee9; border-radius: 10px; }
.card h2 { margin: 0 0 8px; font-size: 16px; color: #0b7285; }
.formula { margin: 6px 0; padding: 8px 10px; background: #f0f4f8; border-radius: 6px;
  font-family: "SFMono-Regular", Consolas, monospace; font-size: 14px; }
.note { margin: 6px 0 0; font-size: 13px; color: #616e7c; }
section.example { margin-top: 24px; padding: 18px 20px; background: #ffffff;
  border: 1px solid #d8dee9; border-radius: 10px; }
section.example h2 { margin: 0 0 10px; font-size: 18px; }
section.example ol { margin: 0; padding-left: 22px; font-size: 14px; }
section.example li { margin-bottom: 8px; }
"""


def to_int(value: object, name: str) -> int:
    """把外部输入转换为整数，拒绝布尔值、小数与非法文本。"""
    if isinstance(value, bool):
        raise ValueError("%s 不能是布尔值" % name)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value) or value != int(value):
            raise ValueError("%s 必须是整数" % name)
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError("%s 不能为空" % name)
        try:
            return int(text)
        except ValueError:
            raise ValueError("%s 必须是整数，收到 %r" % (name, value)) from None
    raise ValueError("%s 必须是整数，收到 %r" % (name, value))


def _make_box_question(number: int, rng: random.Random) -> Question:
    length = float(rng.randint(2, 12))
    width = float(rng.randint(2, 12))
    height = float(rng.randint(2, 12))
    volume = box_volume(length, width, height)
    surface = box_surface(length, width, height)
    prompt = (
        "一个长方体长 %g、宽 %g、高 %g（单位：厘米），求它的体积与表面积"
        "（体积用立方厘米，表面积用平方厘米，各保留 2 位小数）。"
        % (length, width, height)
    )
    answer = "体积 %.2f 立方厘米，表面积 %.2f 平方厘米" % (volume, surface)
    working = (
        "V = 长×宽×高 = %g×%g×%g = %.2f；"
        "S = 2×(长×宽+长×高+宽×高) = 2×(%g+%g+%g) = %.2f。"
        % (
            length,
            width,
            height,
            volume,
            length * width,
            length * height,
            width * height,
            surface,
        )
    )
    return Question(number, "长方体", prompt, answer, working)


def _make_cube_question(number: int, rng: random.Random) -> Question:
    edge = float(rng.randint(2, 10))
    volume = cube_volume(edge)
    surface = cube_surface(edge)
    prompt = (
        "一个正方体的棱长是 %g 厘米，求它的体积与表面积"
        "（体积用立方厘米，表面积用平方厘米，各保留 2 位小数）。" % edge
    )
    answer = "体积 %.2f 立方厘米，表面积 %.2f 平方厘米" % (volume, surface)
    working = (
        "V = 棱长³ = %g³ = %.2f；S = 6×棱长² = 6×%g² = %.2f。"
        % (edge, volume, edge, surface)
    )
    return Question(number, "正方体", prompt, answer, working)


def _make_cylinder_question(number: int, rng: random.Random) -> Question:
    radius = float(rng.randint(1, 6))
    height = float(rng.randint(2, 12))
    volume = cylinder_volume(radius, height)
    surface = cylinder_surface(radius, height)
    prompt = (
        "一个圆柱的底面半径是 %g 厘米、高是 %g 厘米，求它的体积与表面积"
        "（表面积包含两个底面，π 取 3.1415926，保留 2 位小数）。" % (radius, height)
    )
    answer = "体积 %.2f 立方厘米，表面积 %.2f 平方厘米" % (volume, surface)
    working = (
        "V = πr²h = π×%g²×%g ≈ %.2f；"
        "S = 2πr² + 2πrh = 2π×%g×(%g+%g) ≈ %.2f。"
        % (radius, height, volume, radius, radius, height, surface)
    )
    return Question(number, "圆柱", prompt, answer, working)


def _make_cone_question(number: int, rng: random.Random) -> Question:
    radius = float(rng.randint(1, 6))
    height = float(rng.randint(2, 12))
    volume = cone_volume(radius, height)
    surface = cone_surface(radius, height)
    slant = cone_slant_height(radius, height)
    prompt = (
        "一个圆锥的底面半径是 %g 厘米、高是 %g 厘米，求它的体积与表面积"
        "（表面积包含底面，母线长用勾股定理计算，保留 2 位小数）。" % (radius, height)
    )
    answer = "体积 %.2f 立方厘米，表面积 %.2f 平方厘米" % (volume, surface)
    working = (
        "母线 l = √(r²+h²) = √(%g²+%g²) ≈ %.2f；"
        "V = πr²h÷3 = π×%g²×%g÷3 ≈ %.2f；"
        "S = πr² + πrl = π×%g² + π×%g×%.2f ≈ %.2f。"
        % (
            radius,
            height,
            slant,
            radius,
            height,
            volume,
            radius,
            radius,
            slant,
            surface,
        )
    )
    return Question(number, "圆锥", prompt, answer, working)


def _make_sphere_question(number: int, rng: random.Random) -> Question:
    radius = float(rng.randint(1, 8))
    volume = sphere_volume(radius)
    surface = sphere_surface(radius)
    prompt = (
        "一个球的半径是 %g 厘米，求它的体积与表面积"
        "（体积用立方厘米，表面积用平方厘米，各保留 2 位小数）。" % radius
    )
    answer = "体积 %.2f 立方厘米，表面积 %.2f 平方厘米" % (volume, surface)
    working = (
        "V = 4πr³÷3 = 4π×%g³÷3 ≈ %.2f；S = 4πr² = 4π×%g² ≈ %.2f。"
        % (radius, volume, radius, surface)
    )
    return Question(number, "球", prompt, answer, working)


def make_questions(count: int, seed: int) -> List[Question]:
    """按固定顺序生成练习纸题目。

    ``count`` 为 1..50 的整数，``seed`` 决定随机序列；
    相同种子得到完全相同的题目，便于批改与复现。
    """
    total = to_int(count, "题目数量")
    if total < 1 or total > 50:
        raise ValueError("题目数量必须在 1 到 50 之间")
    rng = random.Random(to_int(seed, "随机种子"))
    builders = (
        _make_box_question,
        _make_cube_question,
        _make_cylinder_question,
        _make_cone_question,
        _make_sphere_question,
    )
    questions: List[Question] = []
    for index in range(total):
        builder = builders[index % len(builders)]
        questions.append(builder(index + 1, rng))
    return questions


def _check_questions(questions: Sequence[Question]) -> List[Question]:
    """校验题目列表，空列表与错误类型直接报错。"""
    if questions is None:
        raise ValueError("题目列表不能为空")
    if isinstance(questions, (str, bytes)):
        raise ValueError("题目列表格式不正确")
    try:
        items = list(questions)
    except TypeError:
        raise ValueError("题目列表格式不正确") from None
    if not items:
        raise ValueError("题目列表不能为空")
    return items


def _document(title: str, css: str, body: str) -> str:
    """拼接完整的 HTML 文档。"""
    parts: List[str] = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % html.escape(title),
        "<style>",
        css.strip(),
        "</style>",
        "</head>",
        "<body>",
        body,
        "</body>",
        "</html>",
        "",
    ]
    return "\n".join(parts)


def render_sheet(questions: Sequence[Question], answers: bool = False) -> str:
    """渲染 A4 练习纸；``answers`` 为 True 时附答案与解题过程。"""
    items = _check_questions(questions)
    body: List[str] = []
    body.append('<main class="sheet">')
    body.append("<header>")
    body.append("<h1>立体图形的体积与表面积练习纸</h1>")
    body.append(
        '<p class="meta">共 %d 题　班级：__________　姓名：__________　日期：__________</p>'
        % len(items)
    )
    body.append("</header>")
    body.append('<ol class="questions">')
    for question in items:
        body.append("<li>")
        body.append('<p class="prompt">%s</p>' % html.escape(question.prompt))
        if answers:
            body.append('<p class="answer">答案：%s</p>' % html.escape(question.answer))
            body.append('<p class="working">过程：%s</p>' % html.escape(question.working))
        else:
            body.append('<div class="blank"></div>')
        body.append("</li>")
    body.append("</ol>")
    body.append(
        '<footer class="tips">提示：V 表示体积（立方单位），S 表示表面积（平方单位）；'
        "圆柱、圆锥与球的公式中 π 取 3.1415926，结果保留 2 位小数。</footer>"
    )
    body.append("</main>")
    return _document("立体图形的体积与表面积练习纸", SHEET_CSS, "\n".join(body))


def _svg_box() -> str:
    """手写 SVG：长方体示意图（长、宽、高三个方向）。"""
    lines: List[str] = [
        '<svg viewBox="0 0 220 180" role="img" aria-label="长方体示意图">',
        '<polygon points="25,75 125,75 125,155 25,155" fill="#e7f5ff" '
        'stroke="#1971c2" stroke-width="2" />',
        '<polygon points="25,75 70,35 170,35 125,75" fill="#d0ebff" '
        'stroke="#1971c2" stroke-width="2" />',
        '<polygon points="125,75 170,35 170,115 125,155" fill="#a5d8ff" '
        'stroke="#1971c2" stroke-width="2" />',
        '<text x="75" y="171" font-size="12" fill="#1f2933" '
        'text-anchor="middle">长 a</text>',
        '<text x="11" y="120" font-size="12" fill="#1f2933" '
        'text-anchor="middle">高 h</text>',
        '<text x="160" y="30" font-size="12" fill="#1f2933" '
        'text-anchor="middle">宽 b</text>',
        "</svg>",
    ]
    return "\n".join(lines)


def _svg_cube() -> str:
    """手写 SVG：正方体示意图。"""
    lines: List[str] = [
        '<svg viewBox="0 0 220 180" role="img" aria-label="正方体示意图">',
        '<polygon points="45,70 135,70 135,160 45,160" fill="#e7f5ff" '
        'stroke="#1971c2" stroke-width="2" />',
        '<polygon points="45,70 85,30 175,30 135,70" fill="#d0ebff" '
        'stroke="#1971c2" stroke-width="2" />',
        '<polygon points="135,70 175,30 175,120 135,160" fill="#a5d8ff" '
        'stroke="#1971c2" stroke-width="2" />',
        '<text x="90" y="175" font-size="12" fill="#1f2933" '
        'text-anchor="middle">棱长 a</text>',
        "</svg>",
    ]
    return "\n".join(lines)


def _svg_cylinder() -> str:
    """手写 SVG：圆柱示意图（上下两个椭圆底面）。"""
    lines: List[str] = [
        '<svg viewBox="0 0 220 180" role="img" aria-label="圆柱示意图">',
        '<path d="M 60 45 A 50 16 0 0 1 160 45 L 160 130 '
        'A 50 16 0 0 1 60 130 Z" fill="#e7f5ff" stroke="#1971c2" stroke-width="2" />',
        '<ellipse cx="110" cy="45" rx="50" ry="16" fill="#d0ebff" '
        'stroke="#1971c2" stroke-width="2" />',
        '<line x1="110" y1="45" x2="160" y2="45" stroke="#52606d" '
        'stroke-width="1.2" stroke-dasharray="4 4" />',
        '<text x="135" y="38" font-size="12" fill="#1f2933" '
        'text-anchor="middle">r</text>',
        '<text x="171" y="92" font-size="12" fill="#1f2933">h</text>',
        '<line x1="60" y1="150" x2="160" y2="150" stroke="#52606d" '
        'stroke-width="1.2" stroke-dasharray="4 4" />',
        "</svg>",
    ]
    return "\n".join(lines)


def _svg_cone() -> str:
    """手写 SVG：圆锥示意图（母线、底面半径与高）。"""
    lines: List[str] = [
        '<svg viewBox="0 0 220 180" role="img" aria-label="圆锥示意图">',
        '<ellipse cx="110" cy="135" rx="55" ry="17" fill="#d0ebff" '
        'stroke="#1971c2" stroke-width="2" />',
        '<line x1="110" y1="30" x2="55" y2="135" stroke="#1971c2" stroke-width="2" />',
        '<line x1="110" y1="30" x2="165" y2="135" stroke="#1971c2" stroke-width="2" />',
        '<line x1="110" y1="30" x2="110" y2="135" stroke="#52606d" '
        'stroke-width="1.2" stroke-dasharray="4 4" />',
        '<line x1="110" y1="135" x2="165" y2="135" stroke="#52606d" '
        'stroke-width="1.2" stroke-dasharray="4 4" />',
        '<text x="140" y="60" font-size="12" fill="#1f2933">l</text>',
        '<text x="114" y="90" font-size="12" fill="#1f2933">h</text>',
        '<text x="137" y="152" font-size="12" fill="#1f2933">r</text>',
        "</svg>",
    ]
    return "\n".join(lines)


def _svg_sphere() -> str:
    """手写 SVG：球示意图（赤道用椭圆表示）。"""
    lines: List[str] = [
        '<svg viewBox="0 0 220 180" role="img" aria-label="球示意图">',
        '<circle cx="110" cy="90" r="58" fill="#e7f5ff" '
        'stroke="#1971c2" stroke-width="2" />',
        '<ellipse cx="110" cy="90" rx="58" ry="20" fill="none" '
        'stroke="#1971c2" stroke-width="1.4" stroke-dasharray="5 4" />',
        '<line x1="110" y1="90" x2="168" y2="90" stroke="#52606d" '
        'stroke-width="1.2" stroke-dasharray="4 4" />',
        '<text x="139" y="84" font-size="12" fill="#1f2933" '
        'text-anchor="middle">r</text>',
        "</svg>",
    ]
    return "\n".join(lines)


def render_demo() -> str:
    """渲染演示页：五种立体的简图、公式卡片与例题。"""
    example_box = (3.0, 4.0, 5.0)
    example_cylinder = (2.0, 5.0)
    example_cone = (2.0, 6.0)
    body: List[str] = []
    body.append('<div class="wrap">')
    body.append("<header>")
    body.append("<h1>立体图形的体积与表面积</h1>")
    body.append(
        '<p class="sub">体积描述物体占多大空间，表面积描述物体外表一共有多大；'
        "计算时先认清图形的尺寸，再代入对应公式。</p>"
    )
    body.append("</header>")

    body.append('<div class="figures">')
    figures: List[Tuple[str, str, str]] = [
        ("长方体", _svg_box(), "V = abh，S = 2(ab+ah+bh)"),
        ("正方体", _svg_cube(), "V = a³，S = 6a²"),
        ("圆柱", _svg_cylinder(), "V = πr²h，S = 2πr²+2πrh"),
        ("圆锥", _svg_cone(), "V = πr²h÷3，S = πr²+πrl"),
        ("球", _svg_sphere(), "V = 4πr³÷3，S = 4πr²"),
    ]
    for name, svg, caption in figures:
        body.append("<figure>")
        body.append(svg)
        body.append("<figcaption>%s：%s</figcaption>" % (html.escape(name), html.escape(caption)))
        body.append("</figure>")
    body.append("</div>")

    body.append('<div class="cards">')
    cards: List[Tuple[str, str, str]] = [
        (
            "长方体",
            "V = a × b × h　　S = 2(ab + ah + bh)",
            "长、宽、高三个方向互相垂直；表面积是六个面的面积之和。",
        ),
        (
            "正方体",
            "V = a³　　S = 6a²",
            "正方体是长、宽、高都相等的长方体。",
        ),
        (
            "圆柱",
            "V = πr²h　　S = 2πr² + 2πrh",
            "侧面展开是长方形，长是底面周长 2πr，宽是高 h。",
        ),
        (
            "圆锥",
            "V = πr²h ÷ 3　　S = πr² + πrl　　l = √(r²+h²)",
            "同底等高的圆锥体积是圆柱的三分之一。",
        ),
        (
            "球",
            "V = 4πr³ ÷ 3　　S = 4πr²",
            "球的表面积等于它大圆面积的 4 倍。",
        ),
    ]
    for title, formula, note in cards:
        body.append('<section class="card">')
        body.append("<h2>%s</h2>" % html.escape(title))
        body.append('<p class="formula">%s</p>' % html.escape(formula))
        body.append('<p class="note">%s</p>' % html.escape(note))
        body.append("</section>")
    body.append("</div>")

    body.append('<section class="example">')
    body.append("<h2>例题</h2>")
    body.append("<ol>")
    body.append(
        "<li>长 %g、宽 %g、高 %g 的长方体：V = %.2f 立方单位，S = %.2f 平方单位。</li>"
        % (
            example_box[0],
            example_box[1],
            example_box[2],
            box_volume(*example_box),
            box_surface(*example_box),
        )
    )
    body.append(
        "<li>底面半径 %g、高 %g 的圆柱：V = %.2f 立方单位，S = %.2f 平方单位。</li>"
        % (
            example_cylinder[0],
            example_cylinder[1],
            cylinder_volume(*example_cylinder),
            cylinder_surface(*example_cylinder),
        )
    )
    body.append(
        "<li>底面半径 %g、高 %g 的圆锥：母线 l = %.2f，V = %.2f 立方单位，S = %.2f 平方单位。</li>"
        % (
            example_cone[0],
            example_cone[1],
            cone_slant_height(*example_cone),
            cone_volume(*example_cone),
            cone_surface(*example_cone),
        )
    )
    body.append(
        "<li>半径 3 的球：V = %.2f 立方单位，S = %.2f 平方单位。</li>"
        % (sphere_volume(3.0), sphere_surface(3.0))
    )
    body.append("</ol>")
    body.append("</section>")
    body.append("</div>")
    return _document("立体图形的体积与表面积演示", DEMO_CSS, "\n".join(body))


def write_output(path: str, content: str) -> None:
    """把文本写入文件（UTF-8）；路径非法或写入失败时抛出中文 ``ValueError``。"""
    if not isinstance(path, str):
        raise ValueError("输出路径必须是字符串")
    target = path.strip()
    if not target:
        raise ValueError("输出路径不能为空")
    try:
        with open(target, "w", encoding="utf-8") as handle:
            handle.write(content)
    except OSError as exc:
        raise ValueError("写入文件失败：%s" % exc) from None


__all__ = [
    "Question",
    "make_questions",
    "render_demo",
    "render_sheet",
    "to_int",
    "write_output",
]
