"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_file.read().splitlines()
        self._input_lines = []
        input_file.seek(0)
        for line in input_file.read().splitlines():
            line = re.sub(r"[\n\t\s]*", "", line)
            line = line.split("/")[0]
            if line and not line[0] == "/":
                self._input_lines.append(line)

        self._line_num = -1
        self._cur_inst = ""
        self._symbol = None
        self._dest = None
        self._comp = None
        self._jump = None
        self.advance()

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self._line_num < len(self._input_lines)

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        self._line_num += 1
        if not self.has_more_commands():
            return
        self._cur_inst = self._input_lines[self._line_num]
        cmd = self.command_type()
        if cmd == "A_COMMAND":
            self._symbol = self._cur_inst[1:]
            self._dest = None
            self._comp = None
            self._jump = None
        elif cmd == "C_COMMAND":
            self._symbol = None
            if "=" in self._cur_inst and ";" in self._cur_inst:
                self._dest, temp = self._cur_inst.split("=")
                self._comp, self._jump = temp.split(";")
            elif "=" in self._cur_inst:
                self._dest, self._comp = self._cur_inst.split("=")
                self._jump = None
            elif ";" in self._cur_inst:
                self._comp, self._jump = self._cur_inst.split(";")
                self._dest = None
            else:
                self._comp = self._cur_inst
                self._dest = None
                self._jump = None
        else:
            self._symbol = self._cur_inst[1:-1]
            self._dest = None
            self._comp = None
            self._jump = None

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if self._cur_inst[0] == "@":
            return "A_COMMAND"
        elif self._cur_inst[0] == "(":
            return "L_COMMAND"
        else:
            return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        return self._symbol

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        return self._dest

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        return self._comp

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        return self._jump
