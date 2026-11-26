"""立体图形体积与表面积的核心计算。

本模块只使用标准库。所有对外函数都会校验参数，
非法输入统一抛出中文 ``ValueError``，方便命令行层转成退出码 2。
"""

import math

# 边长、半径、高的取值范围：大于 0 且不超过 1e6
MAX_LENGTH: float = 1e6

# 计算结果的安全上限
MAX_RESULT: float = 1e15


def to_float(value: object, name: str) -> float:
    """把外部输入转换为浮点数。

    拒绝布尔值（bool 不算数值）、空字符串、非数字文本、
    NaN 与正负无穷大；转换失败时抛出中文 ``ValueError``。
    """
    if isinstance(value, bool):
        raise ValueError("%s 不能是布尔值" % name)
    if isinstance(value, (int, float)):
        try:
            result = float(value)
        except OverflowError:
            raise ValueError("%s 数值过大，无法处理" % name) from None
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError("%s 不能为空" % name)
        try:
            result = float(text)
        except ValueError:
            raise ValueError("%s 必须是数字，收到 %r" % (name, value)) from None
    else:
        raise ValueError("%s 必须是数字，收到 %r" % (name, value))
    if not math.isfinite(result):
        raise ValueError("%s 不能是 NaN 或无穷大" % name)
    return result


def check_length(value: object, name: str) -> float:
    """校验长度类参数：必须大于 0 且不超过 1e6。"""
    length = to_float(value, name)
    if length <= 0.0:
        raise ValueError("%s 必须大于 0" % name)
    if length > MAX_LENGTH:
        raise ValueError("%s 不能超过 1000000" % name)
    return length


def check_result(value: float, name: str) -> float:
    """确保结果有限且不超过安全上限。"""
    if not math.isfinite(value):
        raise ValueError("%s 计算结果无效" % name)
    if abs(value) >= MAX_RESULT:
        raise ValueError("%s 超出可计算范围" % name)
    return value


def box_volume(length: float, width: float, height: float) -> float:
    """长方体体积：``V = 长 × 宽 × 高``。"""
    a = check_length(length, "长")
    b = check_length(width, "宽")
    c = check_length(height, "高")
    return check_result(a * b * c, "长方体体积")


def box_surface(length: float, width: float, height: float) -> float:
    """长方体表面积：``S = 2 × (长×宽 + 长×高 + 宽×高)``。"""
    a = check_length(length, "长")
    b = check_length(width, "宽")
    c = check_length(height, "高")
    return check_result(2.0 * (a * b + a * c + b * c), "长方体表面积")


def cube_volume(edge: float) -> float:
    """正方体体积：``V = 棱长³``。"""
    a = check_length(edge, "棱长")
    return check_result(a * a * a, "正方体体积")


def cube_surface(edge: float) -> float:
    """正方体表面积：``S = 6 × 棱长²``。"""
    a = check_length(edge, "棱长")
    return check_result(6.0 * a * a, "正方体表面积")


def cylinder_volume(radius: float, height: float) -> float:
    """圆柱体积：``V = π × r² × h``。"""
    r = check_length(radius, "底面半径")
    h = check_length(height, "高")
    return check_result(math.pi * r * r * h, "圆柱体积")


def cylinder_surface(radius: float, height: float) -> float:
    """圆柱表面积（含两个底面）：``S = 2πr² + 2πrh``。"""
    r = check_length(radius, "底面半径")
    h = check_length(height, "高")
    return check_result(2.0 * math.pi * r * (r + h), "圆柱表面积")


def cone_slant_height(radius: float, height: float) -> float:
    """圆锥母线长：``l = √(r² + h²)``，用勾股定理计算并检查有限性。"""
    r = check_length(radius, "底面半径")
    h = check_length(height, "高")
    slant = math.hypot(r, h)
    return check_result(slant, "圆锥母线")


def cone_volume(radius: float, height: float) -> float:
    """圆锥体积：``V = π × r² × h ÷ 3``。"""
    r = check_length(radius, "底面半径")
    h = check_length(height, "高")
    return check_result(math.pi * r * r * h / 3.0, "圆锥体积")


def cone_surface(radius: float, height: float) -> float:
    """圆锥表面积（含底面）：``S = πr² + πrl``，``l`` 为母线。"""
    r = check_length(radius, "底面半径")
    h = check_length(height, "高")
    slant = cone_slant_height(r, h)
    return check_result(math.pi * r * (r + slant), "圆锥表面积")


def sphere_volume(radius: float) -> float:
    """球体积：``V = 4πr³ ÷ 3``。"""
    r = check_length(radius, "半径")
    return check_result(4.0 * math.pi * r * r * r / 3.0, "球体积")


def sphere_surface(radius: float) -> float:
    """球表面积：``S = 4πr²``。"""
    r = check_length(radius, "半径")
    return check_result(4.0 * math.pi * r * r, "球表面积")


__all__ = [
    "MAX_LENGTH",
    "MAX_RESULT",
    "box_surface",
    "box_volume",
    "check_length",
    "check_result",
    "cone_slant_height",
    "cone_surface",
    "cone_volume",
    "cube_surface",
    "cube_volume",
    "cylinder_surface",
    "cylinder_volume",
    "sphere_surface",
    "sphere_volume",
    "to_float",
]
