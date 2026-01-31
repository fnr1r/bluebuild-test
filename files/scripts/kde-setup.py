#!/usr/bin/env python3

import os
import sys

from abc import ABC, abstractmethod
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

PathLike: TypeAlias = Path | str | os.PathLike

ENCODING = "UTF-8"

KDE_CONF_DIR = Path("/usr/share/kde-settings/kde-profile/default")


def eprint(*args: object):
    print(*args, file=sys.stderr)


def configparser_readfile(path: PathLike) -> ConfigParser:
    config = ConfigParser(allow_unnamed_section=False)
    config.optionxform = str  # type: ignore
    config.read(path, encoding=ENCODING)
    return config


def configparser_writefile(config: ConfigParser, path: PathLike):
    with open(path, "wt", encoding=ENCODING) as file:
        config.write(file, space_around_delimiters=False)


class Change(ABC):
    @abstractmethod
    def apply(self, config: ConfigParser): ...


@dataclass
class ForceReplace(Change):
    section: str
    key: str
    value_initial: str
    value_target: str

    def __str__(self) -> str:
        return "In section {}, key {}, replace {} with {}".format(
            self.section,
            self.key,
            repr(self.value_initial),
            repr(self.value_target),
        )

    def apply(self, config: ConfigParser):
        value_current = config.get(self.section, self.key)
        if value_current == self.value_initial:
            config.set(self.section, self.key, self.value_target)
            return
        msg = "Expected {}, got {}.".format(
            repr(self.value_initial),
            repr(value_current),
        )
        raise ValueError(msg)


ChangeList: TypeAlias = list[Change]

CHANGES_SHARE_CONFIG_KDEGLOBALS: ChangeList = [
    ForceReplace("Icons", "Theme", "breeze", "breeze-dark"),
]
CHANGES_XDG_KDEGLOBALS: ChangeList = [
    ForceReplace("Icons", "Theme", "breeze", "breeze-dark"),
    ForceReplace(
        "KDE",
        "LookAndFeelPackage",
        "org.fedoraproject.fedora.desktop",
        "org.kde.breezedark.desktop",
    ),
    ForceReplace("KDE", "ColorScheme", "BreezeLight", "BreezeDark"),
]

PATCHES: list[tuple[str, ChangeList]] = [
    ("share/config/kdeglobals", CHANGES_SHARE_CONFIG_KDEGLOBALS),
    ("xdg/kdeglobals", CHANGES_XDG_KDEGLOBALS),
]


@dataclass
class FailureFlag:
    failed: bool


def patch_file(path: PathLike, changes: ChangeList, flag: FailureFlag):
    path = Path(path)
    print(f"--- Editing file {path}")
    if not path.exists():
        eprint("File doesn't exist!")
        flag.failed = True
        return
    config = configparser_readfile(path)
    for i, change in enumerate(changes):
        try:
            change.apply(config)
        except Exception as e:
            eprint(f"⊢---- CHANGE {i + 1} FAILED!")
            eprint(f"∟> {change}")
            eprint(e)
            flag.failed = True
    configparser_writefile(config, path)


def main():
    os.chdir(KDE_CONF_DIR)
    flag = FailureFlag(False)
    for path, changes in PATCHES:
        patch_file(path, changes, flag)
    if flag.failed:
        eprint("Configuring KDE Plasma failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
