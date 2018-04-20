import json, logging
from urllib.request import Request, urlopen
from lxml import html

from ..models import RusTbotStore

class RustorkaHotStorage():
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }
    PREURL = "http://rustorka.com/forum"

    @staticmethod
    def get_data():
        return RusTbotStore.get_last(20)

    @staticmethod
    def update():
        try:
            r = Request(RustorkaHotStorage.PREURL + "/viewforum.php?f=1840", headers=RustorkaHotStorage.HEADERS)
            content = urlopen(r).read()

            new_data = []
            tree = html.fromstring(content).xpath("//*[@id='forum-table']//tr[@id]")
            for tr in tree:
                try:
                    #_id = tr.attrib["id"]
                    #_icon = self.PREURL + tr.xpath(".//img[@class='topic_icon']")[0].attrib["src"][1:]
                    _title = tr.xpath(".//a[@class='topictitle']")[0].text
                    _link = RustorkaHotStorage.PREURL + tr.xpath(".//a[@class='topictitle']")[0].attrib["href"][1:]
                    _author = tr.xpath("./td/p/a")[0].text

                    new_data.append({"title": _title,
                                     "link": _link,
                                     "author": _author
                                     })
                except Exception:
                    logging.exception("TBStorage udpate")
                    return []

            return RusTbotStore.store_entries(new_data)
        except Exception:
            return []
            pass
