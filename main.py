#!/usr/bin/python

import argparse
import csv
import re
import sys
from typing import AnyStr, List

from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument(
    "--orig",
    type=str,
    help="С какого языка произвести перевод, копировать в точности из файла перевода!"
)
parser.add_argument(
    "--to",
    type=str,
    help="На какой язык перевести, копировать в точности из файла перевода."
)
parser.add_argument(
    "--filename",
    type=str,
    default="index.html",
    help="Название входного html файла"
)
parser.add_argument(
    "--out_filename",
    type=str,
    default="out.html",
    help="Название html выходного файла"
)
parser.add_argument(
    "--translate_filename",
    type=str,
    default="translate.csv",
    help="Название файла переводов csv"
)
namespace = parser.parse_args()


def check_args() -> None:
    """
    Проверяет переданные аргументы скрипта
    """
    if namespace.orig is None:
        sys.stdout.write("Argument `orig` is required!")
        sys.exit()
    if namespace.to is None:
        sys.stdout.write("Argument `to` is required!")
        sys.exit()


def check_translate_args(row: dict) -> None:
    """
    Проверяет переданные аргументы скрипта переводов
    """
    if row.get(namespace.orig, None) is None:
        sys.stdout.write(f"Invalid `{namespace.orig}`")
        sys.exit()
    if row.get(namespace.to, None) is None:
        sys.stdout.write(f"Invalid `{namespace.to}`")
        sys.exit()


def get_translate(filename: str) -> dict:
    """
    Получает словарь с изначальными и выходными переводами из файла переводов
    """
    out = {}
    with open(filename, encoding='utf8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            check_translate_args(row)
            if row[namespace.orig] == "":
                continue
            out[row[namespace.orig]] = row[namespace.to]

        return out


def read_html() -> List[AnyStr]:
    """
    Читает входной html файл
    """
    with open(namespace.filename, "r", encoding="utf8") as f:
        contents = f.readlines()

    return contents


def translate_html(contents: List[AnyStr], data_translate: dict) -> BeautifulSoup:
    """
    Переводит html в необходимый перевод
    """
    for original_translate, out_translate in data_translate.items():
        for i, content in enumerate(contents):
            ts = original_translate.replace("(", "\\(").replace(")", "\\)").replace("?", "\?").replace(".", "\.")
            if re.findall(ts, content):
                res = re.sub(ts, out_translate, content)
                contents.insert(i, res)
                contents.remove(content)
    soup = BeautifulSoup("".join(contents), "html.parser")

    return soup


def write_finally_html(soup: BeautifulSoup) -> None:
    """
    Записывает готовый html
    """
    with open(namespace.out_filename, 'w', encoding='utf8') as fp:
        fp.write(soup.prettify())


def main():
    check_args()
    data_translate = get_translate(namespace.translate_filename)
    contents = read_html()
    soup = translate_html(contents, data_translate)
    write_finally_html(soup)


if __name__ == '__main__':
    sys.stdout.write('Run...\n')
    main()
    sys.stdout.write("Done!")
