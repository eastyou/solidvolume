"""solidvolume 的单元测试，仅使用标准库 unittest。"""

import html.parser
import io
import math
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from typing import List, Optional, Tuple

from solidvolume import (
    MAX_LENGTH,
    MAX_RESULT,
    Question,
    __version__,
    box_surface,
    box_volume,
    check_length,
    cone_slant_height,
    cone_surface,
    cone_volume,
    cube_surface,
    cube_volume,
    cylinder_surface,
    cylinder_volume,
    make_questions,
    render_demo,
    render_sheet,
    sphere_surface,
    sphere_volume,
    to_float,
    write_output,
)
from solidvolume.cli import build_parser, main
from solidvolume.sheet import to_int


class _TagCollector(html.parser.HTMLParser):
    """收集 HTML 起始标签，用于确认页面结构可被解析。"""

    def __init__(self) -> None:
        super().__init__()
        self.tags: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        self.tags.append(tag)


def _parse_html(text: str) -> _TagCollector:
    collector = _TagCollector()
    collector.feed(text)
    collector.close()
    return collector


def _run_cli(args: List[str]) -> Tuple[int, str, str]:
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(list(args))
    return code, out.getvalue(), err.getvalue()


def _write_temp(content: str) -> str:
    """把内容写入临时文件并返回路径，调用方负责删除。"""
    handle = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".html", delete=False
    )
    with handle:
        handle.write(content)
    return handle.name


class TestConstants(unittest.TestCase):
    def test_version(self) -> None:
        self.assertEqual(__version__, "0.1.0")

    def test_max_length(self) -> None:
        self.assertEqual(MAX_LENGTH, 1e6)

    def test_max_result(self) -> None:
        self.assertEqual(MAX_RESULT, 1e15)


class TestToFloat(unittest.TestCase):
    def test_accepts_int(self) -> None:
        self.assertEqual(to_float(7, "数值"), 7.0)

    def test_accepts_float(self) -> None:
        self.assertEqual(to_float(2.5, "数值"), 2.5)

    def test_accepts_numeric_string_with_spaces(self) -> None:
        self.assertEqual(to_float("  12.5 ", "数值"), 12.5)

    def test_accepts_negative(self) -> None:
        self.assertEqual(to_float("-3", "数值"), -3.0)

    def test_rejects_bool(self) -> None:
        with self.assertRaises(ValueError):
            to_float(True, "数值")

    def test_rejects_empty_string(self) -> None:
        with self.assertRaises(ValueError):
            to_float("", "数值")

    def test_rejects_blank_string(self) -> None:
        with self.assertRaises(ValueError):
            to_float("   ", "数值")

    def test_rejects_text(self) -> None:
        with self.assertRaises(ValueError):
            to_float("abc", "数值")

    def test_rejects_nan(self) -> None:
        with self.assertRaises(ValueError):
            to_float(float("nan"), "数值")

    def test_rejects_infinity(self) -> None:
        with self.assertRaises(ValueError):
            to_float(float("inf"), "数值")

    def test_rejects_none(self) -> None:
        with self.assertRaises(ValueError):
            to_float(None, "数值")


class TestCheckLength(unittest.TestCase):
    def test_accepts_positive(self) -> None:
        self.assertEqual(check_length("3", "长"), 3.0)

    def test_accepts_upper_limit(self) -> None:
        self.assertEqual(check_length(1e6, "长"), 1e6)

    def test_rejects_zero(self) -> None:
        with self.assertRaises(ValueError):
            check_length(0, "长")

    def test_rejects_negative(self) -> None:
        with self.assertRaises(ValueError):
            check_length(-1, "长")

    def test_rejects_above_limit(self) -> None:
        with self.assertRaises(ValueError):
            check_length(1e6 + 1, "长")

    def test_rejects_bool(self) -> None:
        with self.assertRaises(ValueError):
            check_length(False, "长")


class TestBox(unittest.TestCase):
    def test_volume(self) -> None:
        self.assertAlmostEqual(box_volume(3, 4, 5), 60.0)

    def test_surface(self) -> None:
        self.assertAlmostEqual(box_surface(3, 4, 5), 94.0)

    def test_volume_decimal(self) -> None:
        self.assertAlmostEqual(box_volume(2.5, 3, 4), 30.0)

    def test_surface_decimal(self) -> None:
        self.assertAlmostEqual(box_surface(2.5, 3, 4), 59.0)

    def test_unit_values(self) -> None:
        self.assertAlmostEqual(box_volume(1, 1, 1), 1.0)
        self.assertAlmostEqual(box_surface(1, 1, 1), 6.0)

    def test_zero_length_rejected(self) -> None:
        with self.assertRaises(ValueError):
            box_volume(0, 4, 5)

    def test_negative_width_rejected(self) -> None:
        with self.assertRaises(ValueError):
            box_surface(3, -4, 5)

    def test_too_large_rejected(self) -> None:
        with self.assertRaises(ValueError):
            box_volume(1000001, 1, 1)

    def test_result_overflow_rejected(self) -> None:
        with self.assertRaises(ValueError):
            box_volume(1e6, 1e6, 1e6)


class TestCube(unittest.TestCase):
    def test_volume(self) -> None:
        self.assertAlmostEqual(cube_volume(3), 27.0)

    def test_surface(self) -> None:
        self.assertAlmostEqual(cube_surface(3), 54.0)

    def test_half_edge(self) -> None:
        self.assertAlmostEqual(cube_volume(0.5), 0.125)
        self.assertAlmostEqual(cube_surface(0.5), 1.5)

    def test_zero_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cube_volume(0)

    def test_negative_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cube_surface(-2)

    def test_overflow_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cube_volume(1e6)


class TestCylinder(unittest.TestCase):
    def test_volume(self) -> None:
        self.assertAlmostEqual(cylinder_volume(2, 5), math.pi * 4 * 5)

    def test_surface(self) -> None:
        self.assertAlmostEqual(cylinder_surface(2, 5), 2 * math.pi * 2 * 7)

    def test_zero_radius_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cylinder_volume(0, 5)

    def test_zero_height_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cylinder_surface(2, 0)

    def test_negative_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cylinder_volume(-2, 5)

    def test_too_large_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cylinder_volume(2, 1000001)

    def test_overflow_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cylinder_volume(1e6, 1e6)


class TestCone(unittest.TestCase):
    def test_slant_height(self) -> None:
        self.assertAlmostEqual(cone_slant_height(3, 4), 5.0)

    def test_slant_height_two_six(self) -> None:
        self.assertAlmostEqual(cone_slant_height(2, 6), math.sqrt(40.0))

    def test_volume(self) -> None:
        self.assertAlmostEqual(cone_volume(2, 6), math.pi * 4 * 6 / 3.0)

    def test_surface(self) -> None:
        expected = math.pi * 2 * (2 + math.sqrt(40.0))
        self.assertAlmostEqual(cone_surface(2, 6), expected)

    def test_volume_is_one_third_of_cylinder(self) -> None:
        self.assertAlmostEqual(cone_volume(2, 6) * 3, cylinder_volume(2, 6))

    def test_zero_radius_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cone_volume(0, 6)

    def test_negative_height_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cone_surface(2, -6)

    def test_slant_too_large_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cone_slant_height(1000001, 1)

    def test_overflow_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cone_volume(1e6, 1e6)


class TestSphere(unittest.TestCase):
    def test_volume(self) -> None:
        self.assertAlmostEqual(sphere_volume(3), 36 * math.pi)

    def test_surface(self) -> None:
        self.assertAlmostEqual(sphere_surface(3), 36 * math.pi)

    def test_half_radius(self) -> None:
        self.assertAlmostEqual(sphere_volume(0.5), 4 * math.pi * 0.125 / 3.0)
        self.assertAlmostEqual(sphere_surface(0.5), math.pi)

    def test_zero_rejected(self) -> None:
        with self.assertRaises(ValueError):
            sphere_volume(0)

    def test_negative_rejected(self) -> None:
        with self.assertRaises(ValueError):
            sphere_surface(-3)

    def test_overflow_rejected(self) -> None:
        with self.assertRaises(ValueError):
            sphere_volume(1e6)


class TestMakeQuestions(unittest.TestCase):
    def test_count(self) -> None:
        self.assertEqual(len(make_questions(8, 1)), 8)

    def test_count_one(self) -> None:
        questions = make_questions(1, 1)
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].number, 1)

    def test_count_fifty(self) -> None:
        self.assertEqual(len(make_questions(50, 1)), 50)

    def test_seed_reproducible(self) -> None:
        first = make_questions(10, 7)
        second = make_questions(10, 7)
        self.assertEqual([q.prompt for q in first], [q.prompt for q in second])
        self.assertEqual([q.answer for q in first], [q.answer for q in second])

    def test_different_seed_differs(self) -> None:
        first = make_questions(10, 1)
        second = make_questions(10, 2)
        self.assertNotEqual([q.prompt for q in first], [q.prompt for q in second])

    def test_numbers_are_sequential(self) -> None:
        numbers = [q.number for q in make_questions(6, 3)]
        self.assertEqual(numbers, [1, 2, 3, 4, 5, 6])

    def test_five_kinds_covered(self) -> None:
        kinds = set(q.kind for q in make_questions(10, 1))
        self.assertEqual(kinds, {"长方体", "正方体", "圆柱", "圆锥", "球"})

    def test_count_zero_rejected(self) -> None:
        with self.assertRaises(ValueError):
            make_questions(0, 1)

    def test_count_above_limit_rejected(self) -> None:
        with self.assertRaises(ValueError):
            make_questions(51, 1)

    def test_count_text_rejected(self) -> None:
        with self.assertRaises(ValueError):
            make_questions("abc", 1)

    def test_count_bool_rejected(self) -> None:
        with self.assertRaises(ValueError):
            make_questions(True, 1)

    def test_seed_text_rejected(self) -> None:
        with self.assertRaises(ValueError):
            make_questions(3, "seed")


class TestQuestionContent(unittest.TestCase):
    def test_prompt_not_empty(self) -> None:
        for question in make_questions(5, 4):
            self.assertTrue(question.prompt.strip())

    def test_answer_mentions_volume_and_surface(self) -> None:
        for question in make_questions(5, 4):
            self.assertIn("体积", question.answer)
            self.assertIn("表面积", question.answer)

    def test_working_not_empty(self) -> None:
        for question in make_questions(5, 4):
            self.assertTrue(question.working.strip())

    def test_kind_in_known_set(self) -> None:
        known = {"长方体", "正方体", "圆柱", "圆锥", "球"}
        for question in make_questions(5, 4):
            self.assertIn(question.kind, known)


class TestToInt(unittest.TestCase):
    def test_accepts_int(self) -> None:
        self.assertEqual(to_int(8, "题数"), 8)

    def test_accepts_numeric_string(self) -> None:
        self.assertEqual(to_int(" 12 ", "题数"), 12)

    def test_rejects_float(self) -> None:
        with self.assertRaises(ValueError):
            to_int(1.5, "题数")

    def test_rejects_bool(self) -> None:
        with self.assertRaises(ValueError):
            to_int(True, "题数")

    def test_rejects_empty(self) -> None:
        with self.assertRaises(ValueError):
            to_int("  ", "题数")


class TestRenderSheet(unittest.TestCase):
    def test_parseable_html(self) -> None:
        text = render_sheet(make_questions(3, 1))
        collector = _parse_html(text)
        self.assertIn("html", collector.tags)
        self.assertIn("ol", collector.tags)

    def test_doctype_present(self) -> None:
        self.assertTrue(render_sheet(make_questions(2, 1)).startswith("<!DOCTYPE html>"))

    def test_without_answers(self) -> None:
        text = render_sheet(make_questions(3, 1), answers=False)
        self.assertNotIn("答案：", text)
        self.assertIn("blank", text)

    def test_with_answers(self) -> None:
        text = render_sheet(make_questions(3, 1), answers=True)
        self.assertIn("答案：", text)
        self.assertIn("过程：", text)

    def test_empty_list_rejected(self) -> None:
        with self.assertRaises(ValueError):
            render_sheet([])

    def test_none_rejected(self) -> None:
        with self.assertRaises(ValueError):
            render_sheet(None)

    def test_string_rejected(self) -> None:
        with self.assertRaises(ValueError):
            render_sheet("题目")

    def test_special_characters_escaped(self) -> None:
        question = Question(1, "长方体", "<script>x</script>", "答案", "过程")
        text = render_sheet([question], answers=True)
        self.assertNotIn("<script>", text)
        self.assertIn("&lt;script&gt;", text)

    def test_title_present(self) -> None:
        self.assertIn("立体图形的体积与表面积练习纸", render_sheet(make_questions(1, 1)))


class TestRenderDemo(unittest.TestCase):
    def test_parseable_html(self) -> None:
        collector = _parse_html(render_demo())
        self.assertIn("html", collector.tags)
        self.assertIn("svg", collector.tags)

    def test_contains_five_figures(self) -> None:
        self.assertEqual(render_demo().count("<figure>"), 5)

    def test_contains_all_names(self) -> None:
        text = render_demo()
        for name in ("长方体", "正方体", "圆柱", "圆锥", "球"):
            self.assertIn(name, text)

    def test_contains_formulas(self) -> None:
        self.assertIn("πr²h", render_demo())

    def test_has_aria_labels(self) -> None:
        self.assertGreaterEqual(render_demo().count('aria-label="'), 5)

    def test_doctype_present(self) -> None:
        self.assertTrue(render_demo().startswith("<!DOCTYPE html>"))


class TestWriteOutput(unittest.TestCase):
    def test_writes_utf8(self) -> None:
        path = os.path.join(tempfile.gettempdir(), "solidvolume_write_test.html")
        try:
            write_output(path, "体积 60.00")
            with open(path, "r", encoding="utf-8") as handle:
                self.assertEqual(handle.read(), "体积 60.00")
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_empty_path_rejected(self) -> None:
        with self.assertRaises(ValueError):
            write_output("  ", "内容")

    def test_non_string_path_rejected(self) -> None:
        with self.assertRaises(ValueError):
            write_output(123, "内容")

    def test_missing_directory_rejected(self) -> None:
        path = os.path.join(tempfile.gettempdir(), "solidvolume_no_such_dir", "a.html")
        with self.assertRaises(ValueError):
            write_output(path, "内容")

    def test_directory_path_rejected(self) -> None:
        with self.assertRaises(ValueError):
            write_output(tempfile.gettempdir(), "内容")


class TestCliCalculations(unittest.TestCase):
    def test_box(self) -> None:
        code, out, _ = _run_cli(["box", "--length", "3", "--width", "4", "--height", "5"])
        self.assertEqual(code, 0)
        self.assertIn("60.00", out)
        self.assertIn("94.00", out)

    def test_cube(self) -> None:
        code, out, _ = _run_cli(["cube", "--edge", "3"])
        self.assertEqual(code, 0)
        self.assertIn("27.00", out)
        self.assertIn("54.00", out)

    def test_cylinder(self) -> None:
        code, out, _ = _run_cli(["cylinder", "--radius", "2", "--height", "5"])
        self.assertEqual(code, 0)
        self.assertIn("62.83", out)
        self.assertIn("87.96", out)

    def test_cone(self) -> None:
        code, out, _ = _run_cli(["cone", "--radius", "2", "--height", "6"])
        self.assertEqual(code, 0)
        self.assertIn("25.13", out)
        self.assertIn("52.30", out)

    def test_sphere(self) -> None:
        code, out, _ = _run_cli(["sphere", "--radius", "3"])
        self.assertEqual(code, 0)
        self.assertIn("113.10", out)
        self.assertIn("113.10", out)

    def test_box_text_rejected(self) -> None:
        code, _, err = _run_cli(["box", "--length", "abc", "--width", "4", "--height", "5"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_box_zero_rejected(self) -> None:
        code, _, err = _run_cli(["box", "--length", "0", "--width", "4", "--height", "5"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_cube_negative_rejected(self) -> None:
        code, _, err = _run_cli(["cube", "--edge", "-3"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_cylinder_too_large_rejected(self) -> None:
        code, _, err = _run_cli(["cylinder", "--radius", "2", "--height", "2000000"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_cone_zero_rejected(self) -> None:
        code, _, err = _run_cli(["cone", "--radius", "0", "--height", "6"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_sphere_nan_rejected(self) -> None:
        code, _, err = _run_cli(["sphere", "--radius", "nan"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_sphere_overflow_rejected(self) -> None:
        code, _, err = _run_cli(["sphere", "--radius", "1000000"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)


class TestCliFiles(unittest.TestCase):
    def test_sheet_writes_file(self) -> None:
        path = os.path.join(tempfile.gettempdir(), "solidvolume_sheet_test.html")
        try:
            code, out, _ = _run_cli(["sheet", "--count", "8", "--seed", "1", "-o", path])
            self.assertEqual(code, 0)
            self.assertIn("题目数：8", out)
            self.assertTrue(os.path.exists(path))
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_sheet_answers_writes_answers(self) -> None:
        path = os.path.join(tempfile.gettempdir(), "solidvolume_answers_test.html")
        try:
            code, out, _ = _run_cli(
                ["sheet", "--count", "4", "--seed", "2", "--answers", "-o", path]
            )
            self.assertEqual(code, 0)
            self.assertIn("答案：含", out)
            with open(path, "r", encoding="utf-8") as handle:
                self.assertIn("答案：", handle.read())
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_sheet_invalid_count_rejected(self) -> None:
        path = os.path.join(tempfile.gettempdir(), "solidvolume_bad_count.html")
        code, _, err = _run_cli(["sheet", "--count", "0", "-o", path])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_sheet_empty_output_rejected(self) -> None:
        code, _, err = _run_cli(["sheet", "--count", "2", "-o", "   "])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_sheet_missing_directory_rejected(self) -> None:
        path = os.path.join(tempfile.gettempdir(), "solidvolume_no_dir", "sheet.html")
        code, _, err = _run_cli(["sheet", "--count", "2", "-o", path])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_demo_writes_file(self) -> None:
        path = os.path.join(tempfile.gettempdir(), "solidvolume_demo_test.html")
        try:
            code, out, _ = _run_cli(["demo", "-o", path])
            self.assertEqual(code, 0)
            self.assertIn("已生成演示页", out)
            self.assertTrue(os.path.exists(path))
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_demo_output_parseable(self) -> None:
        path = os.path.join(tempfile.gettempdir(), "solidvolume_demo_parse.html")
        try:
            _run_cli(["demo", "-o", path])
            with open(path, "r", encoding="utf-8") as handle:
                text = handle.read()
            collector = _parse_html(text)
            self.assertIn("svg", collector.tags)
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_same_seed_same_content(self) -> None:
        first = os.path.join(tempfile.gettempdir(), "solidvolume_seed_a.html")
        second = os.path.join(tempfile.gettempdir(), "solidvolume_seed_b.html")
        try:
            _run_cli(["sheet", "--count", "6", "--seed", "5", "-o", first])
            _run_cli(["sheet", "--count", "6", "--seed", "5", "-o", second])
            with open(first, "r", encoding="utf-8") as handle:
                text_a = handle.read()
            with open(second, "r", encoding="utf-8") as handle:
                text_b = handle.read()
            self.assertEqual(text_a, text_b)
        finally:
            for path in (first, second):
                if os.path.exists(path):
                    os.remove(path)

    def test_different_seed_different_content(self) -> None:
        first = os.path.join(tempfile.gettempdir(), "solidvolume_seed_c.html")
        second = os.path.join(tempfile.gettempdir(), "solidvolume_seed_d.html")
        try:
            _run_cli(["sheet", "--count", "6", "--seed", "1", "-o", first])
            _run_cli(["sheet", "--count", "6", "--seed", "2", "-o", second])
            with open(first, "r", encoding="utf-8") as handle:
                text_a = handle.read()
            with open(second, "r", encoding="utf-8") as handle:
                text_b = handle.read()
            self.assertNotEqual(text_a, text_b)
        finally:
            for path in (first, second):
                if os.path.exists(path):
                    os.remove(path)


class TestCliArguments(unittest.TestCase):
    def test_help_exits_zero(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            with redirect_stdout(io.StringIO()):
                main(["--help"])
        self.assertEqual(caught.exception.code, 0)

    def test_version_exits_zero(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            with redirect_stdout(io.StringIO()):
                main(["--version"])
        self.assertEqual(caught.exception.code, 0)

    def test_missing_argument_exits_two(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            with redirect_stderr(io.StringIO()):
                main(["cube"])
        self.assertEqual(caught.exception.code, 2)

    def test_unknown_command_exits_two(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            with redirect_stderr(io.StringIO()):
                main(["pyramid", "--edge", "3"])
        self.assertEqual(caught.exception.code, 2)

    def test_parser_has_all_commands(self) -> None:
        parser = build_parser()
        actions = [
            action
            for action in parser._actions
            if hasattr(action, "choices") and action.choices
        ]
        self.assertTrue(actions)


if __name__ == "__main__":
    unittest.main()
