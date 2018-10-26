import logging
import re
from lxml import html
from project.modules.webparser import WebParser
from urllib.parse import urlencode


class TolokaWebParser(WebParser):
    HOST = "https://toloka.to"

    TAG_HD = 0x1

    class Container:
        def __init__(self,
                     title_a="",
                     title_b="",
                     year=0,
                     link="",
                     tag=0x0):
            self.title_a = title_a
            self.title_b = title_b
            self.link = link
            self.year = year
            self.tag = tag

    @classmethod
    def parse_poster(cls, url):
        try:
            content = cls.sync_request(url)
            return cls.link_from_xnode(html.fromstring(content).xpath("//table[@class='forumline']//*[@class='postbody']//img")[0])
        except Exception:
            logging.exception("parse_poster")

        return None

    @classmethod
    def parse_page(cls, url_params=None):
        try:
            logging.debug("toloka parser request top_hd search:")
            content = cls.sync_request("/tracker.php?{}".format(urlencode(url_params)))

            new_data = []
            tree = html.fromstring(content).xpath("//table[contains(@class,'forumline')]//tr[@class]")

            logging.debug("toloka parser begin parsing search:")
            for tr in tree:
                try:
                    a = tr.xpath("./td[contains(@class,'topictitle')]//a[contains(@class,'genmed')]")[0]
                    link = cls.link_from_xnode(a)
                    btext = cls.text_from_xnode(a.xpath(".//b")[0])

                    pars = [item.strip() for item in btext.split("/")]
                    title_a = pars[0]
                    title_b = ""

                    groups = None
                    for item in pars:
                        groups = re.search("(.*)( )(\([0-9]+)", item)
                        if groups:
                            try:
                                title_b = groups.group(1)
                            except Exception:
                                raise Exception
                            break

                    try:
                        year = int(groups.group(3)[1:5])
                    except Exception:
                        raise Exception

                    new_data.append(cls.Container(title_a=title_a,
                                                  title_b=title_b,
                                                  year=year,
                                                  link=link,
                                                  tag=cls.TAG_HD))
                except Exception:
                    logging.exception("TolokaWebParser udpate")

            logging.debug("toloka parser return search:")
            return new_data
        except Exception:
            logging.exception("get_hot")
            return []
