import logging
import re
from urllib import request
from urllib.request import Request, urlopen
from lxml import html
import html as _html


class WebParser:
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/65.0.3325.181 Safari/537.36"
    }
    
    HOST = ""

    @classmethod
    def sync_request(cls, url) -> [bytes, None]:
        logging.debug("web parser request")
        r = Request(cls.beatify_url(url), headers=cls.HEADERS)
        try:
            return urlopen(r).read()
        except request.URLError:
            return None

    @classmethod
    def beatify_url(cls, url, is_https=False):
        if url[0] == '.':
            url = url[1:]

        res = ""

        if re.search("^http", url):
            res = url
        elif re.search("^//", url):
            res = "http:"+url if re.search("^http:", cls.HOST) else "https:"+url
        elif re.search("^/", url):
            res = cls.HOST+url
        else:
            res = cls.HOST+"/"+url

        if is_https:
            res = re.sub("^http:", "https:", res)
        return res

    @classmethod
    def link_from_xnode(cls, node, is_https=False):
        if "href" in node.attrib:
            link = node.attrib["href"]
        elif "src" in node.attrib:
            link = node.attrib["src"]
        else:
            return None

        return cls.beatify_url(link, is_https=is_https)

    @staticmethod
    def text_from_xnode(node):
        s = html.tostring(node, pretty_print=True).decode("utf-8")
        str = _html.unescape(s).strip()
        return re.sub("<.*?>", "", str)
