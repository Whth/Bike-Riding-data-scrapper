import os

from ttbikeSpider import ttbikeSpider

ttbike = ttbikeSpider(token="",
                      path=os.getcwd(),
                      city="温州市",
                      cityCode="0577",
                      adCode="330304",
                      timeout=6,
                      nums=2
                      )
ttbike.test()
