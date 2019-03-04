import logging
from lxml import html
from project.modules.webparser import WebParser
from project.modules.map import Map


class KinoWebParser(WebParser):
    HOST = "http://kinozal.tv"

    TAG_HD = 0x1

    @classmethod
    def parse_top(cls):
        try:
            content = cls.sync_request("/top.php?t=0&d=11&k=0&f=2&w=1&s=0")

            new_data = []
            tree = html.fromstring(content).xpath("//div[contains(@class,'bx1')]/a")
            for a in tree:
                try:
                    link = cls.link_from_xnode(a)
                    poster = cls.link_from_xnode(a.xpath(".//img")[0])

                    title_ru, title_en = "", ""
                    text = a.attrib["title"]
                    items = [s.strip() for s in text.split("/")]
                    try:
                        year = int(items[2][:4])
                        title_en = items[1]
                        title_ru = items[0]
                    except IndexError:
                        year = int(items[1][:4])
                        title_ru = items[0]

                    new_data.append(Map(title_ru=title_ru,
                                        title_en=title_en,
                                        year=year,
                                        poster=poster,
                                        link=link,
                                        tag=cls.TAG_HD))
                except Exception as e:
                    logging.exception("TBStorage udpate: {}".format(e))

            return new_data
        except Exception as e:
            logging.exception("get_hot: {}".format(e))
            return []
