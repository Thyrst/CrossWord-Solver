#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
API for krizovky-slovnik.cz
"""
#
#= Imports ====================================================================
import lxml.html
from urllib.request import urlopen
from urllib.parse import urlencode


#= Functions ==================================================================
def get_answers(hint, chars=0):
    """
    returns list of results for czech crossword hints
    you can specify length of result
    """
    # check args
    hint = str(hint).strip()
    try:
        chars = int(chars)
    except ValueError:
        raise ValueError("`chars` must be int")

    # prepare url
    data = {"co": hint}
    data = urlencode(data)
    url = "http://krizovky-slovnik.cz/krizovka?" + data

    # save page to variable
    page = urlopen(url).read()
    page = str(page, "utf8")

    # parse html
    page = lxml.html.fromstring(page)
    # get list of results
    results = page.xpath("//body//table//tr")
    # remove heading row
    results = results[1:]

    # check if there are some results
    text = results[0].xpath("./td/text()")[0]
    if text.startswith("Nebyla nalezena"):
        # return empty list if no results found
        return list()

    if chars > 0:
        # check results
        # if number of character of result is set
        check = True
    else:
        check = False

    # put results into list
    ret = list()

    for res in results:
        if check:
            # parse lentgh of result from page
            length = res.xpath("./td/text()")[0]
            length = length.strip()
            length = length.split()[1] # "na x písmen"
            length = int(length)

            # filter results by their length
            if length != chars:
                continue

        # parse the final text
        text = res.xpath("./td/text()")[1]

        ret += [text.strip()]

    return ret


#= Main program ===============================================================
if __name__ == '__main__':
    """
    prints list of results
    1st argument is number of chars ('ch' is 1 char)
    next arguments are hint
    """
    from sys import argv

    results = get_answers(" ".join(argv[2:]), argv[1])

    print(", ".join(results))
