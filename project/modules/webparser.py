import logging
import re
from urllib.request import Request, urlopen
from lxml import html
import html as _html

class WebParser(object):
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }

    @staticmethod
    def sync_request(url):
        logging.debug("web parser request")
        r = Request(url, headers=WebParser.HEADERS)
        content = urlopen(r).read()

        return content

    @staticmethod
    def link_from_xnode(node, host=""):
        if "href" in node.attrib:
            str = node.attrib["href"]
        elif "src" in node.attrib:
            str = node.attrib["src"]
        else:
            return None

        if str[0] == '.':
            str = str[1:]

        if re.search("^http", str):
            return str
        elif re.search("^//", str):
            return "http:"+str if re.search("^http:", host) else "https:"+str
        elif re.search("^/", str):
            return host+str
        else:
            return host+"/"+str

    @staticmethod
    def text_from_xnode(node):
        s = html.tostring(node, pretty_print=True).decode("utf-8")
        str = _html.unescape(s).strip()
        return re.sub("<.*?>", "", str)