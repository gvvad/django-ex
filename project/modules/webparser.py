import logging
import re
from urllib.request import Request, urlopen
from lxml import html
import html as _html


class WebParser(object):
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }
    
    HOST = ""

    @classmethod
    def sync_request(cls, url):
        logging.debug("web parser request")
        r = Request(cls.beatify_url(url), headers=cls.HEADERS)
        content = urlopen(r).read()

        return content

    @classmethod
    def beatify_url(cls, url):
        if url[0] == '.':
            url = url[1:]

        if re.search("^http", url):
            return url
        elif re.search("^//", url):
            return "http:"+url if re.search("^http:", cls.HOST) else "https:"+url
        elif re.search("^/", url):
            return cls.HOST+url
        else:
            return cls.HOST+"/"+url

    @classmethod
    def link_from_xnode(cls, node):
        if "href" in node.attrib:
            link = node.attrib["href"]
        elif "src" in node.attrib:
            link = node.attrib["src"]
        else:
            return None

        return cls.beatify_url(link)

    @staticmethod
    def text_from_xnode(node):
        s = html.tostring(node, pretty_print=True).decode("utf-8")
        str = _html.unescape(s).strip()
        return re.sub("<.*?>", "", str)