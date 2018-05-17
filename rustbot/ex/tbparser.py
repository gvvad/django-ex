import logging
from lxml import html
from project.modules.webparser import WebParser

class RustorkaWebParser(WebParser):
    HOST = "http://rustorka.com/forum"

    @staticmethod
    def get_hot():
        try:
            content = RustorkaWebParser.sync_request(RustorkaWebParser.HOST + "/viewforum.php?f=1840")

            new_data = []
            tree = html.fromstring(content).xpath("//*[@id='forum-table']//tr[@id]")
            for tr in tree:
                try:
                    _title = RustorkaWebParser.text_from_xnode(tr.xpath(".//a[@class='topictitle']")[0])
                    _link = RustorkaWebParser.link_from_xnode(tr.xpath(".//a[@class='topictitle']")[0], RustorkaWebParser.HOST)
                    _author = RustorkaWebParser.text_from_xnode(tr.xpath("./td/p/a")[0])

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
            content = RustorkaWebParser.sync_request(RustorkaWebParser.HOST + "/viewforum.php?f=1398")

            new_data = []
            tree = html.fromstring(content).xpath("//*[@id='forum-table']//tr[@id]")
            for tr in tree:
                try:
                    a = tr.xpath(".//a[contains(@class,'torTopic')]")[0]

                    _title = RustorkaWebParser.text_from_xnode(a.xpath(".//*")[0])
                    _link = RustorkaWebParser.link_from_xnode(a, RustorkaWebParser.HOST)
                    _author = RustorkaWebParser.text_from_xnode(tr.xpath(".//a[contains(@class,'topicAuthor')]")[0])

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
