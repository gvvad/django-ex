import logging
import re
from lxml import html
from project.modules.webparser import WebParser


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
            self.title_a=title_a
            self.title_b=title_b
            self.link=link
            self.year=year
            self.tag=tag

    @staticmethod
    def parse_poster(url):
        try:
            content = TolokaWebParser.sync_request(url)
            return TolokaWebParser.link_from_xnode(html.fromstring(content).xpath("//table[@class='forumline']//*[@class='postbody']//img")[0],
                                                   TolokaWebParser.HOST)
        except Exception:
            logging.exception("parse_poster")

        return None


    @staticmethod
    def parse_top_hd(search=""):
        try:
            content = TolokaWebParser.sync_request(TolokaWebParser.HOST + "/tracker.php?f=96&nm={}&tm=7".format(search))

            new_data = []
            tree = html.fromstring(content).xpath("//table[contains(@class,'forumline')]//tr[@class]")
            for tr in tree:
                try:
                    a = tr.xpath("./td[contains(@class,'topictitle')]//a[contains(@class,'genmed')]")[0]
                    link = TolokaWebParser.link_from_xnode(a, TolokaWebParser.HOST)
                    btext = TolokaWebParser.text_from_xnode(a.xpath(".//b")[0])

                    pars = [item.strip() for item in btext.split("/")]
                    title_a = pars[0]
                    groups = re.search("(.*)( )(\([0-9]+)", pars[1])
                    try:
                        title_b = groups.group(1)
                    except Exception:
                        raise Exception

                    try:
                        year = int(groups.group(3)[1:5])
                    except Exception:
                        raise Exception

                    new_data.append(TolokaWebParser.Container(title_a=title_a,
                                                            title_b=title_b,
                                                            year=year,
                                                            link=link,
                                                            tag=TolokaWebParser.TAG_HD))
                except Exception:
                    logging.exception("TolokaWebParser udpate")

            return new_data
        except Exception:
            logging.exception("get_hot")
            return []
