import logging
import re
from urllib.request import Request, urlopen
from lxml import html


class TolokaWebParser():
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }
    PREURL = "https://toloka.to"

    TAG_HD = 0x1

    class Container:
        def __init__(self,
                     title_a="",
                     title_b="",
                     year=0,
                     poster="",
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
            r = Request(url, headers=TolokaWebParser.HEADERS)
            content = urlopen(r).read()
            res = html.fromstring(content).xpath("//table[@class='forumline']//*[@class='postbody']//img")[0].attrib["src"]
            if res:
                if re.search("^//", res):
                    res = "http:" + res
                elif re.search("^/", res):
                    res = TolokaWebParser.PREURL + res
                return res

        except Exception:
            logging.exception("parse_poster")

        return None


    @staticmethod
    def parse_top_hd(search=""):
        try:
            logging.debug("parse_top_hd requested")
            r = Request(TolokaWebParser.PREURL + "/tracker.php?f=96&nm={}&tm=7".format(search), headers=TolokaWebParser.HEADERS)
            content = urlopen(r).read()
            logging.debug("Requested success")

            new_data = []
            tree = html.fromstring(content).xpath("//table[contains(@class,'forumline')]//tr[@class]")
            for tr in tree:
                try:
                    a = tr.xpath("./td[contains(@class,'topictitle')]//a[contains(@class,'genmed')]")[0]
                    link = TolokaWebParser.PREURL + "/" + a.attrib["href"]
                    btext = a.xpath(".//b")[0].text

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
