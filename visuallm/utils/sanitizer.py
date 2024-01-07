import re

# TODO: move to singledispatch
from functools import singledispatch
from typing import TypeVar

T = TypeVar("T")


class Sanitizer:
    @staticmethod
    def convert_newline_to_br_tags(value: str):
        value = value.replace("\n", "<br />")
        return value

    @staticmethod
    def convert_brackets(value: str):
        value = value.replace("<", "&lt;")
        value = value.replace(">", "&gt;")
        return value

    @staticmethod
    def convert_backticks(value: str):
        value = re.sub(r"`([^`]*)`", r"<code>\1</code>", value)
        return value

    @staticmethod
    def convert_bold(value: str):
        value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
        return value

    @staticmethod
    def convert_italic(value: str):
        value = re.sub(r"\*(.+?)\*", r"<em>\1</em>", value)
        return value

    @staticmethod
    def is_sane(value: str):
        allowed = [r"<br />", r"<code>", r"</code>", r"<b>", r"</b>", r"<em>", r"</em>"]
        value = re.sub("|".join(allowed), "", value)
        return "<" not in value and ">" not in value

    @singledispatch
    @staticmethod
    def sanitize(value):
        raise NotImplementedError()

    @sanitize.register
    @staticmethod
    def sanitize_int(value: int):
        return Sanitizer.sanitize_str(str(value))

    @sanitize.register
    @staticmethod
    def sanitize_str(value: str):
        value = Sanitizer.convert_brackets(value)
        value = Sanitizer.convert_bold(value)
        value = Sanitizer.convert_italic(value)
        value = Sanitizer.convert_newline_to_br_tags(value)
        value = Sanitizer.convert_backticks(value)
        return value

    @sanitize.register
    @staticmethod
    def sanitize_list_str(values: list) -> list:
        return [Sanitizer.sanitize(value) for value in values]
