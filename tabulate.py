# -*- coding: utf-8 -*-
"""Pretty-print tabular data.
   referencia: https://pypi.python.org/pypi/tabulate"""

from __future__ import print_function
from __future__ import unicode_literals
from collections import namedtuple
from platform import python_version_tuple
import re


if python_version_tuple()[0] < "3":
    from itertools import izip_longest
    from functools import partial
    _none_type = type(None)
    _int_type = int
    _long_type = long
    _float_type = float
    _text_type = unicode
    _binary_type = str

    def _is_file(f):
        return isinstance(f, file)

else:
    from itertools import zip_longest as izip_longest
    from functools import reduce, partial
    _none_type = type(None)
    _int_type = int
    _long_type = int
    _float_type = float
    _text_type = str
    _binary_type = bytes

    import io
    def _is_file(f):
        return isinstance(f, io.IOBase)


__all__ = ["tabulate", "tabulate_formats", "simple_separated_format"]
__version__ = "0.7.5"


MIN_PADDING = 2


Line = namedtuple("Line", ["begin", "hline", "sep", "end"])


DataRow = namedtuple("DataRow", ["begin", "sep", "end"])


# A table structure is suppposed to be:
#
#     --- lineabove ---------
#         headerrow
#     --- linebelowheader ---
#         datarow
#     --- linebewteenrows ---
#     ... (more datarows) ...
#     --- linebewteenrows ---
#         last datarow
#     --- linebelow ---------
#
# TableFormat's line* elements can be
#
#   - either None, if the element is not used,
#   - or a Line tuple,
#   - or a function: [col_widths], [col_alignments] -> string.
#
# TableFormat's *row elements can be
#
#   - either None, if the element is not used,
#   - or a DataRow tuple,
#   - or a function: [cell_values], [col_widths], [col_alignments] -> string.
#
# padding (an integer) is the amount of white space around data values.
#
# with_header_hide:
#
#   - either None, to display all table elements unconditionally,
#   - or a list of elements not to be displayed if the table has column headers.
#
TableFormat = namedtuple("TableFormat", ["lineabove", "linebelowheader",
                                         "linebetweenrows", "linebelow",
                                         "headerrow", "datarow",
                                         "padding", "with_header_hide"])


def _pipe_segment_with_colons(align, colwidth):
    """Return a segment of a horizontal line with optional colons which
    indicate column's alignment (as in `pipe` output format)."""
    w = colwidth
    if align in ["right", "decimal"]:
        return ('-' * (w - 1)) + ":"
    elif align == "center":
        return ":" + ('-' * (w - 2)) + ":"
    elif align == "left":
        return ":" + ('-' * (w - 1))
    else:
        return '-' * w


def _pipe_line_with_colons(colwidths, colaligns):
    """Return a horizontal line with optional colons to indicate column's
    alignment (as in `pipe` output format)."""
    segments = [_pipe_segment_with_colons(a, w) for a, w in zip(colaligns, colwidths)]
    return "|" + "|".join(segments) + "|"

def _mediawiki_row_with_attrs(separator, cell_values, colwidths, colaligns):
    alignment = { "left":    '',
                  "right":   'align="right"| ',
                  "center":  'align="center"| ',
                  "decimal": 'align="right"| ' }
    # hard-coded padding _around_ align attribute and value together
    # rather than padding parameter which affects only the value
    values_with_attrs = [' ' + alignment.get(a, '') + c + ' '
                         for c, a in zip(cell_values, colaligns)]
    colsep = separator*2
    return (separator + colsep.join(values_with_attrs)).rstrip()


def _html_row_with_attrs(celltag, cell_values, colwidths, colaligns):
    alignment = { "left":    '',
                  "right":   ' style="text-align: right;"',
                  "center":  ' style="text-align: center;"',
                  "decimal": ' style="text-align: right;"' }
    values_with_attrs = ["<{0}{1}>{2}</{0}>".format(celltag, alignment.get(a, ''), c)
                         for c, a in zip(cell_values, colaligns)]
    return "<tr>" + "".join(values_with_attrs).rstrip() + "</tr>"


def _latex_line_begin_tabular(colwidths, colaligns, booktabs=False):
    alignment = { "left": "l", "right": "r", "center": "c", "decimal": "r" }
    tabular_columns_fmt = "".join([alignment.get(a, "l") for a in colaligns])
    return "\n".join(["\\begin{tabular}{" + tabular_columns_fmt + "}",
                      "\\toprule" if booktabs else "\hline"])

LATEX_ESCAPE_RULES = {r"&": r"\&", r"%": r"\%", r"$": r"\$", r"#": r"\#",
                      r"_": r"\_", r"^": r"\^{}", r"{": r"\{", r"}": r"\}",
                      r"~": r"\textasciitilde{}", "\\": r"\textbackslash{}",
                      r"<": r"\ensuremath{<}", r">": r"\ensuremath{>}"}


def _latex_row(cell_values, colwidths, colaligns):
    def escape_char(c):
        return LATEX_ESCAPE_RULES.get(c, c)
    escaped_values = ["".join(map(escape_char, cell)) for cell in cell_values]
    rowfmt = DataRow("", "&", "\\\\")
    return _build_simple_row(escaped_values, rowfmt)


_table_formats = {"simple":
                  TableFormat(lineabove=Line("", "-", "  ", ""),
                              linebelowheader=Line("", "-", "  ", ""),
                              linebetweenrows=None,
                              linebelow=Line("", "-", "  ", ""),
                              headerrow=DataRow("", "  ", ""),
                              datarow=DataRow("", "  ", ""),
                              padding=0,
                              with_header_hide=["lineabove", "linebelow"]),
                  "plain":
                  TableFormat(lineabove=None, linebelowheader=None,
                              linebetweenrows=None, linebelow=None,
                              headerrow=DataRow("", "  ", ""),
                              datarow=DataRow("", "  ", ""),
                              padding=0, with_header_hide=None),
                  "grid":
                  TableFormat(lineabove=Line("+", "-", "+", "+"),
                              linebelowheader=Line("+", "=", "+", "+"),
                              linebetweenrows=Line("+", "-", "+", "+"),
                              linebelow=Line("+", "-", "+", "+"),
                              headerrow=DataRow("|", "|", "|"),
                              datarow=DataRow("|", "|", "|"),
                              padding=1, with_header_hide=None),
                  "fancy_grid":
                  TableFormat(lineabove=Line("╒", "═", "╤", "╕"),
                              linebelowheader=Line("╞", "═", "╪", "╡"),
                              linebetweenrows=Line("├", "─", "┼", "┤"),
                              linebelow=Line("╘", "═", "╧", "╛"),

