# //////////////////////////////////////////////////////////////////////////////
from __future__ import annotations

import typing

# //////////////////////////////////////////////////////////////////////////////


class RuntimeBoolExpression:
    class tagExprVar:
        pass

    # --------------------------------------------------------------------
    @staticmethod
    def eval(
        expression: str,
        params: dict[str, tagExprVar],
    ) -> bool:
        assert type(expression) is str
        assert type(params) is dict

        if not expression.strip():
            raise RuntimeError("Expresion is empty.")

        # Создаем контекст парсера (аналог tag_ctx)
        ctx = __class__.tagContext(expression, params)
        __class__._get_token(ctx)

        # Запускаем рекурсивный спуск
        res = __class__._process_1_or(ctx)
        assert type(res) is bool

        if ctx.last_token != "":
            raise RuntimeError(f"Syntax error at {ctx.pos}")

        return res

    # Логика парсера (Recursive Descent) ---------------------------------
    @staticmethod
    def _process_1_or(ctx: tagContext):
        assert type(ctx) is __class__.tagContext
        res = __class__._process_2_and(ctx)
        while ctx.last_token == "||" or ctx.last_token == "or":
            __class__._get_token(ctx)
            res = __class__._process_2_and(ctx) or res
        return res

    # --------------------------------------------------------------------
    @staticmethod
    def _process_2_and(ctx: tagContext):
        assert type(ctx) is __class__.tagContext
        res = __class__._process_3_not(ctx)
        while ctx.last_token == "&&" or ctx.last_token == "and":
            __class__._get_token(ctx)
            res = __class__._process_3_not(ctx) and res
        return res

    # --------------------------------------------------------------------
    @staticmethod
    def _process_3_not(ctx: tagContext):
        assert type(ctx) is __class__.tagContext
        if ctx.last_token in ("!", "not"):
            __class__._get_token(ctx)
            return not __class__._process_4_bracket(ctx)
        return __class__._process_4_bracket(ctx)

    # --------------------------------------------------------------------
    @staticmethod
    def _process_4_bracket(ctx: tagContext):
        assert type(ctx) is __class__.tagContext
        if ctx.last_token == "(":
            __class__._get_token(ctx)
            res = __class__._process_1_or(ctx)
            if ctx.last_token != ")":
                raise RuntimeError("No close bracket")
            __class__._get_token(ctx)
            return res
        return __class__._process_term(ctx)

    # --------------------------------------------------------------------
    @staticmethod
    def _process_term(ctx: tagContext):
        assert type(ctx) is __class__.tagContext

        # Обработка сравнения: IDENT OPERATOR VALUE
        var_name = ctx.last_token  # Например, VERSION
        __class__._get_token(ctx)

        op = ctx.last_token  # Например, >=
        __class__._get_token(ctx)

        val = ctx.last_token  # Например, 1.2.3
        __class__._get_token(ctx)

        # Вызываем твой tagSpecVar
        obj = ctx.params.get(var_name)

        if obj is None:
            raise RuntimeError(f"Unknown ident: {var_name}")

        assert isinstance(obj, __class__.tagExprVar)

        # Магия Python: вызываем оператор по имени
        ops = {
            "==": "__eq__",
            "!=": "__ne__",
            ">": "__gt__",
            "<": "__lt__",
            ">=": "__ge__",
            "<=": "__le__",
        }

        if op not in ops:
            raise RuntimeError(f"Unknown operator: {op}")

        return getattr(obj, ops[op])(val)

    # --- Токенизатор (аналог get_token) ---
    @staticmethod
    def _get_token(ctx: tagContext):
        assert type(ctx) is __class__.tagContext

        ctx.last_token = ""
        # Пропускаем пробелы
        while ctx.pos < len(ctx.text) and ctx.text[ctx.pos].isspace():
            ctx.pos += 1

        if ctx.pos >= len(ctx.text):
            return

        char = ctx.text[ctx.pos]

        # Скобки
        if char in "()":
            ctx.last_token = char
            ctx.pos += 1
        # Операторы (составные)
        elif char in "<>!=|&":
            start = ctx.pos
            while ctx.pos < len(ctx.text) and ctx.text[ctx.pos] in "<>!=|&":
                ctx.pos += 1
            ctx.last_token = ctx.text[start : ctx.pos]  # noqa: E203
        # Идентификаторы и значения (до разделителя)
        else:
            start = ctx.pos
            while ctx.pos < len(ctx.text) and not __class__._is_delim(
                ctx.text[ctx.pos]
            ):  # noqa: E501
                ctx.pos += 1
            # Убираем кавычки если есть
            ctx.last_token = ctx.text[start : ctx.pos].strip("'\"")  # noqa: E203
        return

    # --------------------------------------------------------------------
    @staticmethod
    def _is_delim(ch: str):
        assert type(ch) is str
        assert len(ch) == 1
        return ch.isspace() or ch in "()<>!=|&"

    # --------------------------------------------------------------------
    class tagContext:
        def __init__(
            self,
            text: str,
            params: typing.Dict[str, RuntimeBoolExpression.tagExprVar],
        ):
            assert type(text) is str
            assert type(params) is dict
            self.text = text
            self.params = params
            self.pos = 0
            self.last_token = ""
            return


# //////////////////////////////////////////////////////////////////////////////
