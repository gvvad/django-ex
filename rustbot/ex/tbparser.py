import logging
from urllib.request import Request, urlopen
from lxml import html
import html as _html
import re

class RustorkaWebParser():
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }
    PREURL = "http://rustorka.com/forum"

    @staticmethod
    def get_inner_text(node):
        s = html.tostring(node, pretty_print=True).decode("utf-8")
        str = _html.unescape(s).strip()
        return re.sub("<.*?>", "", str)

    @staticmethod
    def get_hot():
        try:
            logging.debug("get_hot requested")
            r = Request(RustorkaWebParser.PREURL + "/viewforum.php?f=1840", headers=RustorkaWebParser.HEADERS)
            content = urlopen(r).read()
            logging.debug("Requested success")

            new_data = []
            tree = html.fromstring(content).xpath("//*[@id='forum-table']//tr[@id]")
            for tr in tree:
                try:
                    #_id = tr.attrib["id"]
                    #_icon = self.PREURL + tr.xpath(".//img[@class='topic_icon']")[0].attrib["src"][1:]
                    _title = RustorkaWebParser.get_inner_text(tr.xpath(".//a[@class='topictitle']")[0])

                    _link = RustorkaWebParser.PREURL + tr.xpath(".//a[@class='topictitle']")[0].attrib["href"][1:]
                    _author = tr.xpath("./td/p/a")[0].text

                    new_data.append({"title": _title,
                                     "link": _link,
                                     "author": _author
                                     })
                except Exception:
                    logging.exception("TBStorage udpate")

            return new_data
        except Exception:
            logging.exception("get_hot")
            return []

    @staticmethod
    def get_hot_news():
        try:
            logging.debug("get_hot_news requested")
            r = Request(RustorkaWebParser.PREURL + "/viewforum.php?f=1398", headers=RustorkaWebParser.HEADERS)
            content = urlopen(r).read()
            logging.debug("Requested success")

            new_data = []
            tree = html.fromstring(content).xpath("//*[@id='forum-table']//tr[@id]")
            for tr in tree:
                try:
                    # _id = tr.attrib["id"]
                    # _icon = self.PREURL + tr.xpath(".//img[@class='topic_icon']")[0].attrib["src"][1:]
                    a = tr.xpath(".//a[contains(@class,'torTopic')]")[0]
                    _title = RustorkaWebParser.get_inner_text(a.xpath(".//*")[0])
                    _link = RustorkaWebParser.PREURL + a.attrib["href"][1:]
                    _author = tr.xpath(".//a[contains(@class, 'topicAuthor')]")[0].text

                    new_data.append({"title": _title,
                                     "link": _link,
                                     "author": _author
                                     })
                except Exception:
                    logging.exception("TBStorage udpate")

            return new_data
        except Exception:
            logging.exception("get_hot_news")
            return []
