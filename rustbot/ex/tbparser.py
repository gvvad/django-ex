import logging
from lxml import html
from project.modules.webparser import WebParser
import datetime


class RustorkaWebParser(WebParser):
    HOST = "http://rustorka.com/forum"

    @classmethod
    def parse_poster(cls, url):
        """
        Parse post picture
        :param url: page url
        :return: poster pic url
        """
        try:
            content = cls.sync_request(url)
            return cls.link_from_xnode(
                html.fromstring(content).xpath("(//table[@id='topic_main']//td[contains(@class,'message')])[1]"
                                               "//div[@class='post_wrap']//img")[0])
        except IndexError:
            return None

    @classmethod
    def get_hot(cls):
        try:
            content = cls.sync_request("/viewforum.php?f=1840")

            new_data = []
            tree = html.fromstring(content).xpath("//*[@id='forum-table']//tr[@id]")
            for tr in tree:
                try:
                    _title = cls.text_from_xnode(tr.xpath(".//a[@class='topictitle']")[0])
                    _link = cls.link_from_xnode(tr.xpath(".//a[@class='topictitle']")[0])
                    _author = cls.text_from_xnode(tr.xpath("./td/p/a")[0])
                    _s_date = cls.text_from_xnode(tr.xpath("./td/p")[0]).split(" ")[0]

                    # Skip posts earlier then 60 days
                    try:
                        if not (datetime.datetime.strptime(_s_date, "%Y-%m-%d") + datetime.timedelta(60.0))\
                               > datetime.datetime.now():
                            continue
                    except ValueError:
                        pass

                    new_data.append({"title": _title,
                                     "link": _link,
                                     "author": _author})
                except Exception:
                    logging.exception("TBStorage udpate")

            return new_data
        except Exception:
            logging.exception("get_hot")
            return []

    @classmethod
    def get_hot_news(cls):
        try:
            content = cls.sync_request("/viewforum.php?f=1398")

            new_data = []
            tree = html.fromstring(content).xpath("//*[@id='forum-table']//tr[@id]")
            for tr in tree:
                try:
                    a = tr.xpath(".//a[contains(@class,'torTopic')]")[0]

                    _title = cls.text_from_xnode(a.xpath(".//*")[0])
                    _link = cls.link_from_xnode(a)
                    _author = cls.text_from_xnode(tr.xpath(".//a[contains(@class,'topicAuthor')]")[0])

                    new_data.append({"title": _title,
                                     "link": _link,
                                     "author": _author})
                except Exception:
                    logging.exception("TBStorage udpate")

            return new_data
        except Exception:
            logging.exception("get_hot_news")
            return []
