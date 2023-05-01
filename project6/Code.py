"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


class Code:
    """Translates Hack assembly language mnemonics into binary codes."""
    
    @staticmethod
    def dest(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a dest mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        d1 = "0"
        d2 = "0"
        d3 = "0"
        if mnemonic:
            if "A" in mnemonic:
                d1 = "1"
            if "D" in mnemonic:
                d2 = "1"
            if "M" in mnemonic:
                d3 = "1"
        return d1+d2+d3

    @staticmethod
    def comp(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a comp mnemonic string.

        Returns:
            str: the binary code of the given mnemonic.
        """
        a = "0"
        c1 = "0"
        c2 = "0"
        c3 = "0"
        c4 = "0"
        c5 = "0"
        c6 = "0"

        c2_is_zr = {"0", "D", "!D", "-D", "D-1",
                    "D+A", "D+M", "A-D", "M-D", "D&A", "D&M"}
        c4_not_zr = {"1", "D", "!D", "-D", "D+1", "A+1", "M+1",
                     "D-1", "A-D", "M-D", "D|A", "D|M"}
        c6_is_zr = {"0", "-1", "D", "A", "M", "D-1",
                    "A-1", "M-1", "D+A", "D+M", "D&A", "D&M"}

        # Shift options
        if "<<" in mnemonic or ">>" in mnemonic:
            if "A" in mnemonic and "<<" in mnemonic:
                return "0100000"
            if "D" in mnemonic and "<<" in mnemonic:
                return "0110000"
            if "M" in mnemonic and "<<" in mnemonic:
                return "1100000"
            if "A" in mnemonic and ">>" in mnemonic:
                return "0000000"
            if "D" in mnemonic and ">>" in mnemonic:
                return "0010000"
            if "M" in mnemonic and ">>" in mnemonic:
                return "1000000"

        # Other options
        if "M" in mnemonic:
            a = "1"
        if "D" not in mnemonic:
            c1 = "1"
        if mnemonic not in c2_is_zr:
            c2 = "1"
        if "A" not in mnemonic and "M" not in mnemonic:
            c3 = "1"
        if mnemonic in c4_not_zr:
            c4 = "1"
        if "+" in mnemonic or "-" in mnemonic or "1" in mnemonic or "0" in mnemonic:
            c5 = "1"
        if mnemonic not in c6_is_zr:
            c6 = "1"
        return a+c1+c2+c3+c4+c5+c6

    @staticmethod
    def jump(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a jump mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        j1 = "0"
        j2 = "0"
        j3 = "0"
        if mnemonic:
            if "G" not in mnemonic and "Q" not in mnemonic:
                j1 = "1"
            if "T" not in mnemonic and "N" not in mnemonic:
                j2 = "1"
            if "L" not in mnemonic and "Q" not in mnemonic:
                j3 = "1"
        return j1+j2+j3
