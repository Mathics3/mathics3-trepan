# -*- coding: utf-8 -*-
#   Copyright (C) 2024 Rocky Bernstein
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pymathics.trepan.processor.command.base_submgr import SubcommandMgr


class ShowCommand(SubcommandMgr):
    """**show** *subcommand*

    Generic command for showing things about the debugger.  You can
    give unique prefix of the name of a subcommand to get information
    about just that subcommand.

    Type `show` for a list of *show* subcommands and what they do.
    Type `help show *` for just a list of *show* subcommands."""

    short_help = "Show parts of the debugger environment"
    SubcommandMgr.setup(locals(), category="status")


if __name__ == "__main__":
    from pymathics.trepan.processor.command import mock

    d, cp = mock.dbg_setup()
    command = ShowCommand(cp, "show")
    command.run(["show"])
    pass
