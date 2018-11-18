import logging
from lxml import html
from project.modules.webparser import WebParser


class KinoWebParser(WebParser):
    HOST = "http://kinozal.tv"

    TAG_HD = 0x1

    class Container:
        def __init__(self,
                     title_ru="",
                     title_en="",
                     year=0,
                     poster="",
                     link="",
                     tag=0x0):
            self.title_en=title_en
            self.title_ru=title_ru
            self.link=link
            self.year=year
            self.poster=poster
            self.tag=tag

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
                        title_ru = items[0]
                        title_en = items[1]
                    except Exception:
                        try:
                            year = int(items[1][:4])
                            title_ru = items[0]
                        except Exception:
                            raise Exception

                    new_data.append(cls.Container(title_ru=title_ru,
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
