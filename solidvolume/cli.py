"""命令行入口。"""

import argparse
import sys
from typing import List, Optional, Sequence

from . import __version__
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
from .sheet import make_questions, render_demo, render_sheet, write_output


def _ensure_utf8_console() -> None:
    """把标准输出与标准错误尽量切换为 UTF-8，失败时保持原状。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            continue


def build_parser() -> argparse.ArgumentParser:
    """构建命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="solidvolume",
        description="初中数学：立体图形的体积与表面积计算工具。",
    )
    parser.add_argument("--version", action="version", version="solidvolume " + __version__)
    subparsers = parser.add_subparsers(dest="command", required=True, metavar="子命令")

    box = subparsers.add_parser("box", help="计算长方体的体积与表面积")
    box.add_argument("--length", required=True, type=str, metavar="长", help="长，大于 0 且不超过 1000000")
    box.add_argument("--width", required=True, type=str, metavar="宽", help="宽，大于 0 且不超过 1000000")
    box.add_argument("--height", required=True, type=str, metavar="高", help="高，大于 0 且不超过 1000000")

    cube = subparsers.add_parser("cube", help="计算正方体的体积与表面积")
    cube.add_argument("--edge", required=True, type=str, metavar="棱长", help="棱长，大于 0 且不超过 1000000")

    cylinder = subparsers.add_parser("cylinder", help="计算圆柱的体积与表面积")
    cylinder.add_argument("--radius", required=True, type=str, metavar="半径", help="底面半径，大于 0 且不超过 1000000")
    cylinder.add_argument("--height", required=True, type=str, metavar="高", help="高，大于 0 且不超过 1000000")

    cone = subparsers.add_parser("cone", help="计算圆锥的体积与表面积")
    cone.add_argument("--radius", required=True, type=str, metavar="半径", help="底面半径，大于 0 且不超过 1000000")
    cone.add_argument("--height", required=True, type=str, metavar="高", help="高，大于 0 且不超过 1000000")

    sphere = subparsers.add_parser("sphere", help="计算球的体积与表面积")
    sphere.add_argument("--radius", required=True, type=str, metavar="半径", help="半径，大于 0 且不超过 1000000")

    sheet = subparsers.add_parser("sheet", help="生成 A4 练习纸")
    sheet.add_argument("--count", default="8", type=str, metavar="题数", help="题目数量，1 到 50，默认 8")
    sheet.add_argument("--seed", default="1", type=str, metavar="整数", help="随机种子，默认 1")
    sheet.add_argument("-o", "--output", required=True, type=str, metavar="路径", help="输出 HTML 文件")
    sheet.add_argument("--answers", action="store_true", help="在练习纸上附答案与解题过程")

    demo = subparsers.add_parser("demo", help="生成演示页")
    demo.add_argument("-o", "--output", required=True, type=str, metavar="路径", help="输出 HTML 文件")

    return parser


def _run(args: argparse.Namespace) -> int:
    """根据子命令执行计算或生成页面。"""
    command = args.command
    if command == "box":
        length = args.length
        width = args.width
        height = args.height
        volume = box_volume(length, width, height)
        surface = box_surface(length, width, height)
        print("长方体体积：%.2f 立方单位" % volume)
        print("长方体表面积：%.2f 平方单位" % surface)
        print(
            "依据：V = 长×宽×高，S = 2×(长×宽+长×高+宽×高)，"
            "长 %s、宽 %s、高 %s" % (length.strip(), width.strip(), height.strip())
        )
        return 0
    if command == "cube":
        edge = args.edge
        volume = cube_volume(edge)
        surface = cube_surface(edge)
        print("正方体体积：%.2f 立方单位" % volume)
        print("正方体表面积：%.2f 平方单位" % surface)
        print("依据：V = 棱长³，S = 6×棱长²，棱长 %s" % edge.strip())
        return 0
    if command == "cylinder":
        radius = args.radius
        height = args.height
        volume = cylinder_volume(radius, height)
        surface = cylinder_surface(radius, height)
        print("圆柱体积：%.2f 立方单位" % volume)
        print("圆柱表面积：%.2f 平方单位" % surface)
        print(
            "依据：V = πr²h，S = 2πr²+2πrh，半径 %s、高 %s"
            % (radius.strip(), height.strip())
        )
        return 0
    if command == "cone":
        radius = args.radius
        height = args.height
        volume = cone_volume(radius, height)
        surface = cone_surface(radius, height)
        slant = cone_slant_height(radius, height)
        print("圆锥体积：%.2f 立方单位" % volume)
        print("圆锥表面积：%.2f 平方单位" % surface)
        print(
            "依据：V = πr²h÷3，S = πr²+πrl，母线 l = √(r²+h²) ≈ %.2f，"
            "半径 %s、高 %s" % (slant, radius.strip(), height.strip())
        )
        return 0
    if command == "sphere":
        radius = args.radius
        volume = sphere_volume(radius)
        surface = sphere_surface(radius)
        print("球体积：%.2f 立方单位" % volume)
        print("球表面积：%.2f 平方单位" % surface)
        print("依据：V = 4πr³÷3，S = 4πr²，半径 %s" % radius.strip())
        return 0
    if command == "sheet":
        questions = make_questions(args.count, args.seed)
        content = render_sheet(questions, args.answers)
        write_output(args.output, content)
        print("已生成练习纸：%s" % args.output)
        print("题目数：%d，答案：%s" % (len(questions), "含" if args.answers else "不含"))
        return 0
    if command == "demo":
        content = render_demo()
        write_output(args.output, content)
        print("已生成演示页：%s" % args.output)
        return 0
    raise ValueError("未知子命令：%s" % command)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """命令行主函数，返回退出码：成功 0，输入或写入失败 2。"""
    _ensure_utf8_console()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except (TypeError, ValueError) as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2


__all__: List[str] = ["build_parser", "main"]
