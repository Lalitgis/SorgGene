"""
SorghumPost - Region String Parser
=====================================
Parses pasted genomic region strings -- the kind you copy straight out of
a GWAS results table or Manhattan plot -- into (chrom, start, end).

Accepted formats (case-insensitive, commas in numbers are ignored):
    Chr6:34,967,715..35,167,715
    Chr6:34,967,715-35,167,715
    chr6:34967715-35167715
    6:34967715 to 35167715
"""

import re

REGION_PATTERN = re.compile(
    r"^\s*(?:chr)?\s*([^\s:]+?)\s*:\s*([\d,]+)\s*(?:\.\.+|-|–|—|to)\s*([\d,]+)\s*(?:bp)?\s*$",
    re.IGNORECASE,
)


def parse_region(text: str):
    """Parse a single region string into (chrom, start, end).
    Returns None if the string doesn't match a recognized format."""
    if not text:
        return None

    match = REGION_PATTERN.match(text.strip())
    if not match:
        return None

    chrom, start_str, end_str = match.groups()
    try:
        start = int(start_str.replace(",", ""))
        end = int(end_str.replace(",", ""))
    except ValueError:
        return None

    if start > end:
        start, end = end, start

    return chrom, start, end


def parse_regions(text: str):
    """Parse multiple newline-separated region strings.

    Returns (parsed, failed):
        parsed -- list of (chrom, start, end, raw_line) tuples
        failed -- list of raw lines that couldn't be parsed
    """
    parsed = []
    failed = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        result = parse_region(line)
        if result:
            chrom, start, end = result
            parsed.append((chrom, start, end, line))
        else:
            failed.append(line)
    return parsed, failed
