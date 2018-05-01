import logging
from urllib.request import Request, urlopen
from lxml import html


class KinoWebParser():
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }
    PREURL = "http://kinozal.tv"

    class Container:
        def __init__(self,
                     title_ru="",
                     title_en="",
                     year=0,
                     poster="",
                     link="",
                     is_hd=False):
            self.title_en=title_en
            self.title_ru=title_ru
            self.link=link
            self.year=year
            self.poster=poster
            self.is_hd=is_hd

    @staticmethod
    def parse_top():
        try:
            logging.debug("parse_top_hd requested")
            r = Request(KinoWebParser.PREURL + "/top.php?t=0&d=11&k=0&f=2&w=1&s=0", headers=KinoWebParser.HEADERS)
            content = urlopen(r).read()
            logging.debug("Requested success")

            new_data = []
            tree = html.fromstring(content).xpath("//div[contains(@class,'bx1')]/a")
            for a in tree:
                try:
                    poster = a.xpath(".//img")[0].attrib["src"]
                    title_ru, title_en = "", ""
                    year = 0
                    link = KinoWebParser.PREURL + a.attrib["href"]
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

                    new_data.append(KinoWebParser.Container(title_ru=title_ru,
                                                            title_en=title_en,
                                                            year=year,
                                                            poster=poster,
                                                            link=link,
                                                            is_hd=True))
                except Exception:
                    logging.exception("TBStorage udpate")

            return new_data
        except Exception:
            logging.exception("get_hot")
            return []
