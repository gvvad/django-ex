import json, logging, urllib2
from lxml import html


class RustorkaHotStorage():
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }
    PREURL = "http://rustorka.com/forum"

    storage = []

    def __init__(self, fname="rustor.json"):
        self.FILE_NAME = fname

        try:
            with open(self.FILE_NAME, "r") as file:
                self.storage = json.load(file)
        except Exception:
            pass

    def get_data(self):
        return self.storage

    def update(self):
        try:
            text = urllib2.Request(self.PREURL + "/viewforum.php?f=1840", headers=self.HEADERS).read()

            new_data = []
            tree = html.fromstring(text).xpath("//*[@id='forum-table']//tr[@id]")
            for tr in tree:
                try:
                    #_id = tr.attrib["id"]
                    #_icon = self.PREURL + tr.xpath(".//img[@class='topic_icon']")[0].attrib["src"][1:]
                    _title = tr.xpath(".//a[@class='topictitle']")[0].text
                    _link = self.PREURL + tr.xpath(".//a[@class='topictitle']")[0].attrib["href"][1:]
                    _author = tr.xpath("./td/p/a")[0].text

                    new_data.append({"title": _title,
                                     "link": _link,
                                     "author": _author
                                     })
                except Exception:
                    logging.exception("TBStorage udpate")
                    pass

            delta = list(filter(lambda x: x not in self.storage, new_data))
            self.storage = new_data

            try:
                with open(self.FILE_NAME, "w") as file:
                    file.write(json.dumps(self.storage))
            except Exception:
                logging.exception("TBStorage update write file")
                pass

            return delta
        except Exception:
            return []
            pass
