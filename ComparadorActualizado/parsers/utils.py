import re


def searchAndGetMatch(source, regex, ifAbsent=None):
    searchRes = re.search(
        regex,
        source,
    )
    if searchRes is None and ifAbsent is not None:
        return ifAbsent
    return searchRes.groups()[0]


def searchAndGetAllMatches(source, regex):
    searchRes = re.findall(
        regex,
        source,
    )
    return searchRes
