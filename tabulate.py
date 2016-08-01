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
                              headerrow=DataRow("│", "│", "│"),
                              datarow=DataRow("│", "│", "│"),
                              padding=0, with_header_hide=None),
                  "pipe":
                  TableFormat(lineabove=_pipe_line_with_colons,
                              linebelowheader=_pipe_line_with_colons,
                              linebetweenrows=None,
                              linebelow=None,
                              headerrow=DataRow("|", "|", "|"),
                              datarow=DataRow("|", "|", "|"),
                              padding=1,
                              with_header_hide=["lineabove"]),
                  "orgtbl":
                  TableFormat(lineabove=None,
                              linebelowheader=Line("|", "-", "+", "|"),
                              linebetweenrows=None,
                              linebelow=None,
                              headerrow=DataRow("|", "|", "|"),
                              datarow=DataRow("|", "|", "|"),
                              padding=1, with_header_hide=None),
                  "psql":
                  TableFormat(lineabove=Line("+", "-", "+", "+"),
                              linebelowheader=Line("|", "-", "+", "|"),
                              linebetweenrows=None,
                              linebelow=Line("+", "-", "+", "+"),
                              headerrow=DataRow("|", "|", "|"),
                              datarow=DataRow("|", "|", "|"),
                              padding=1, with_header_hide=None),
                  "rst":
                  TableFormat(lineabove=Line("", "=", "  ", ""),
                              linebelowheader=Line("", "=", "  ", ""),
                              linebetweenrows=None,
                              linebelow=Line("", "=", "  ", ""),
                              headerrow=DataRow("", "  ", ""),
                              datarow=DataRow("", "  ", ""),
                              padding=0, with_header_hide=None),
                  "mediawiki":
                  TableFormat(lineabove=Line("{| class=\"wikitable\" style=\"text-align: left;\"",
                                             "", "", "\n|+ <!-- caption -->\n|-"),
                              linebelowheader=Line("|-", "", "", ""),
                              linebetweenrows=Line("|-", "", "", ""),
                              linebelow=Line("|}", "", "", ""),
                              headerrow=partial(_mediawiki_row_with_attrs, "!"),
                              datarow=partial(_mediawiki_row_with_attrs, "|"),
                              padding=0, with_header_hide=None),
                  "html":
                  TableFormat(lineabove=Line("<table>", "", "", ""),
                              linebelowheader=None,
                              linebetweenrows=None,
                              linebelow=Line("</table>", "", "", ""),
                              headerrow=partial(_html_row_with_attrs, "th"),
                              datarow=partial(_html_row_with_attrs, "td"),
                              padding=0, with_header_hide=None),
                  "latex":
                  TableFormat(lineabove=_latex_line_begin_tabular,
                              linebelowheader=Line("\\hline", "", "", ""),
                              linebetweenrows=None,
                              linebelow=Line("\\hline\n\\end{tabular}", "", "", ""),
                              headerrow=_latex_row,
                              datarow=_latex_row,
                              padding=1, with_header_hide=None),
                  "latex_booktabs":
                  TableFormat(lineabove=partial(_latex_line_begin_tabular, booktabs=True),
                              linebelowheader=Line("\\midrule", "", "", ""),
                              linebetweenrows=None,
                              linebelow=Line("\\bottomrule\n\\end{tabular}", "", "", ""),
                              headerrow=_latex_row,
                              datarow=_latex_row,
                              padding=1, with_header_hide=None),
                  "tsv":
                  TableFormat(lineabove=None, linebelowheader=None,
                              linebetweenrows=None, linebelow=None,
                              headerrow=DataRow("", "\t", ""),
                              datarow=DataRow("", "\t", ""),
                              padding=0, with_header_hide=None)}


tabulate_formats = list(sorted(_table_formats.keys()))


_invisible_codes = re.compile(r"\x1b\[\d*m|\x1b\[\d*\;\d*\;\d*m")  # ANSI color codes
_invisible_codes_bytes = re.compile(b"\x1b\[\d*m|\x1b\[\d*\;\d*\;\d*m")  # ANSI color codes


def simple_separated_format(separator):
    """Construct a simple TableFormat with columns separated by a separator.

    >>> tsv = simple_separated_format("\\t") ; \
        tabulate([["foo", 1], ["spam", 23]], tablefmt=tsv) == 'foo \\t 1\\nspam\\t23'
    True

    """
    return TableFormat(None, None, None, None,
                       headerrow=DataRow('', separator, ''),
                       datarow=DataRow('', separator, ''),
                       padding=0, with_header_hide=None)


def _isconvertible(conv, string):
    try:
        n = conv(string)
        return True
    except (ValueError, TypeError):
        return False


def _isnumber(string):
    """
    >>> _isnumber("123.45")
    True
    >>> _isnumber("123")
    True
    >>> _isnumber("spam")
    False
    """
    return _isconvertible(float, string)


def _isint(string, inttype=int):
    """
    >>> _isint("123")
    True
    >>> _isint("123.45")
    False
    """
    return type(string) is inttype or\
           (isinstance(string, _binary_type) or isinstance(string, _text_type))\
            and\
            _isconvertible(inttype, string)


def _type(string, has_invisible=True):
    """The least generic type (type(None), int, float, str, unicode).

    >>> _type(None) is type(None)
    True
    >>> _type("foo") is type("")
    True
    >>> _type("1") is type(1)
    True
    >>> _type('\x1b[31m42\x1b[0m') is type(42)
    True
    >>> _type('\x1b[31m42\x1b[0m') is type(42)
    True

    """

    if has_invisible and \
       (isinstance(string, _text_type) or isinstance(string, _binary_type)):
        string = _strip_invisible(string)

    if string is None:
        return _none_type
    elif hasattr(string, "isoformat"):  # datetime.datetime, date, and time
        return _text_type
    elif _isint(string):
        return int
    elif _isint(string, _long_type):
        return _long_type
    elif _isnumber(string):
        return float
    elif isinstance(string, _binary_type):
        return _binary_type
    else:
        return _text_type


def _afterpoint(string):
    """Symbols after a decimal point, -1 if the string lacks the decimal point.

    >>> _afterpoint("123.45")
    2
    >>> _afterpoint("1001")
    -1
    >>> _afterpoint("eggs")
    -1
    >>> _afterpoint("123e45")
    2

    """
    if _isnumber(string):

