"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self._filename = None
        self._output_stream = output_stream
        self._label_counter = 0

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self._filename = filename
        pass

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        # Your code goes here!
        self._output_stream.write(f"// {command}\n")
        self._decrease_sp(True)

        # one argument commands
        if command in {"not", "neg", "shiftleft", "shifright"}:
            if command == "not":
                self._output_stream.write("M=!M\n")
            elif command == "neg":
                self._output_stream.write("M=-M\n")
            elif command == "shiftleft":
                self._output_stream.write("M=M<<\n")
            else:
                self._output_stream.write("M=M>>\n")
            self._increase_sp()

        # two arguments commands
        else:
            self._output_stream.write("D=M\n")
            if command not in {"eq", "gt", "lt"}:
                self._decrease_sp(True)
            if command == "add":
                self._output_stream.write("D=D+M\n")
            if command == "sub":
                self._output_stream.write("D=M-D\n")
            if command == "and":
                self._output_stream.write("D=D&M\n")
            if command == "or":
                self._output_stream.write("D=D|M\n")
            if command not in {"eq", "gt", "lt"}:
                self._output_stream.write("@SP\n"  # SP = D = result
                                          "A=M\n"
                                          "M=D\n")
            if command == "eq":
                self._compare("JEQ")
            if command == "gt":
                self._compare("JGT")
            if command == "lt":
                self._compare("JLT")

            self._increase_sp()

        self._output_stream.write("\n")

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.
        if command == "C_PUSH":
            self._output_stream.write(f"// push {segment} {index}\n")
            self._push(index, segment)
        else:
            self._output_stream.write(f"// pop {segment} {index}\n")
            self._pop(index, segment)
        self._output_stream.write("\n")

    """
    Comparison procedure:
        * First, check the sign of x and y, if signs are different, compare by signs.
            this step prevents subtraction of numbers which can cause overflow.
        * If signs are the equal, compare by subtraction.
        * Pseudo-Code:
            D = X - Y
            LET RESULT = TRUE
            IF CONDITION: GOTO END
            RESULT=FALSE
            (END)
    """
    def _compare(self, condition: str) -> None:
        # initialize labels
        end_lbl = self._create_label(f"END_{condition}", True)
        equal_sign_lbl = self._create_label(f"EQUAL_SIGN_{condition}")

        # write
        self._compare_signs(condition, end_lbl, equal_sign_lbl)
        self._output_stream.write(f"({equal_sign_lbl})\n")
        self._compare_equal_sign(condition, end_lbl)
        self._output_stream.write(f"({end_lbl})\n")

    """
    y is already popped to D, 
        set R14 true, check if y is greater or equal to 0:
            if so, jump to end of y-check. else: set R14 false and finish y-check.
    pop x to D,
        set R13 true, check if y is greater or equal to 0:
            if so, jump to end of x-check. else: set R13 false and finish x-check.
    compare signs of x and y (R13 to R14),
        if different sign, compare by signs and jump to end comparison label.
        else, continue (to same sign comparison).
    """
    def _compare_signs(self, cond: str, end_lbl: str, equal_sign_lbl: str) -> None:
        # initialize y label
        y_geq_lbl = self._create_label(f"Y_JEQ_{cond}")
        # write
        self._output_stream.write("// R14 = (y >= 0)\n")    # y was already popped: D = y
        self._output_stream.write("@R14\n"
                                  "M=-1\n")
        self._output_stream.write(f"@{y_geq_lbl}\n"
                                  "D;JGE\n")
        self._output_stream.write("@R14\n"
                                  "M=0\n")
        self._output_stream.write(f"({y_geq_lbl})\n")
        
        # initialize x label
        x_geq_lbl = self._create_label(f"X_JEQ_{cond}")
        # write
        self._output_stream.write("// R13 = (x >= 0)\n")
        self._decrease_sp(True)  # A = SP
        self._output_stream.write("D=M\n")  # pop to D
        self._output_stream.write("@R13\n"  
                                  "M=-1\n")
        self._output_stream.write(f"@{x_geq_lbl}\n"
                                  "D;JGE\n")
        self._output_stream.write("@R13\n"
                                  "M=0\n")
        self._output_stream.write(f"({x_geq_lbl})\n")

        self._output_stream.write("// if R13 == R14: goto EQUAL_SIGN label\n")
        self._output_stream.write("@R13\n"
                                  "D=M\n"
                                  "@R14\n"
                                  "D=D-M\n")
        self._output_stream.write(f"@{equal_sign_lbl}\n"
                                  "D;JEQ\n")

        self._output_stream.write("// x and y have different signs -> compare by signs\n")
        self._output_stream.write("@SP\n"
                                  "A=M\n"
                                  "M=-1\n"
                                  "@R14\n")  # R14 = M = (y >= 0)

        if cond != "JGT":
            self._output_stream.write("D=M+1\n")  # if (y >= 0): D = 0, else: D = 1
        else:
            self._output_stream.write("D=M\n")  # if (y >= 0): D = -1, else: D = 0

        self._output_stream.write(f"@{end_lbl}\n"
                                  "D;JEQ\n")
        self._output_stream.write("@SP\n"
                                  "A=M\n"
                                  "M=0\n")
        self._output_stream.write(f"@{end_lbl}\n"
                                  "0;JMP\n")

    """
    code gets here only if x and y are the same signs to prevent overflow.
    compares x and y by subtraction.
    """
    def _compare_equal_sign(self, cond: str, end_lbl: str) -> None:
        self._output_stream.write("@SP\n"
                                  "A=M+1\n"
                                  "D=M\n")  # D = y
        self._output_stream.write("A=A-1\n"
                                  "D=M-D\n")  # D = x - y
        self._output_stream.write("M=-1\n")
        self._output_stream.write(f"@{end_lbl}\n"
                                  f"D;{cond}\n")
        self._output_stream.write("@SP\n"
                                  "A=M\n")
        self._output_stream.write("M=0\n")

    def _create_label(self, name: str, inc: bool = False) -> str:
        if inc:
            self._label_counter += 1
        return f"{name}_{self._label_counter}"

    def _pop(self, index: int, segment: str) -> None:
        if segment == "static":
            self._decrease_sp(True)  # A = SP
            self._output_stream.write("D=M\n"  # D = popped value
                                      f"@{self._filename}.{index}\n"
                                      "M=D\n")
        elif segment == "pointer":
            self._decrease_sp(True)
            if index == 0:
                self._output_stream.write("D=M\n"  # D = popped value
                                          "@THIS\n"
                                          "M=D\n")
            else:
                self._output_stream.write("D=M\n"  # D = popped value
                                          "@THAT\n"
                                          "M=D\n")
        else:
            self._decrease_sp()
            self._get_to_mem(index, segment)  # D = (segment i) address
            self._output_stream.write("@R13\n"  # store (segment i) address in R13 (general purpose register)
                                      "M=D\n")
            self._output_stream.write("@SP\n"  # D = popped value
                                      "A=M\n"
                                      "D=M\n")
            self._output_stream.write("@R13\n"  # segment i = popped value
                                      "A=M\n"
                                      "M=D\n")

    def _push(self, index: int, segment: str) -> None:
        if segment == "constant":
            self._output_stream.write(f"@{index}\n")
            self._output_stream.write("D=A\n")  # D = index
        elif segment == "static":
            self._output_stream.write(f"@{self._filename}.{index}\n"
                                      "D=M\n")  # D = (static i)
        elif segment == "pointer":
            if index == 0:
                self._output_stream.write("@THIS\n"
                                          "D=M\n")
            else:
                self._output_stream.write("@THAT\n"
                                          "D=M\n")
        else:
            self._get_to_mem(index, segment)  # D = (segment i) address
            self._output_stream.write("A=D\n")  # A = (segment i) address
            self._output_stream.write("D=M\n")  # D = (segment i)
        self._output_stream.write("@SP\n"  # SP = pushed value from segment i
                                  "A=M\n"
                                  "M=D\n")
        self._increase_sp()

    def _increase_sp(self) -> None:
        self._output_stream.write("@SP\n"
                                  "M=M+1\n")

    def _decrease_sp(self, set_a: bool = False) -> None:
        self._output_stream.write("@SP\n")
        if set_a:
            self._output_stream.write("M=M-1\n")
            self._output_stream.write("A=M\n")
        else:
            self._output_stream.write("M=M-1\n")

    def _get_to_mem(self, index: int, segment: str) -> None:
        if segment == "temp":
            self._output_stream.write("@5\n"  # D = (temp 0) address
                                      "D=A\n")
        else:
            if segment == "local":
                self._output_stream.write("@LCL\n")
            if segment == "argument":
                self._output_stream.write("@ARG\n")
            if segment == "this":
                self._output_stream.write("@THIS\n")
            if segment == "that":
                self._output_stream.write("@THAT\n")
            self._output_stream.write("D=M\n")  # D = (segment 0) address
        self._output_stream.write(f"@{index}\n"  # D = (segment i) address
                                  "D=D+A\n")

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        pass

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        pass

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        pass
