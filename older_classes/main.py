from ttbikeSpider import ttbikeSpider

ttbike = ttbikeSpider(token="",
                      # path=os.getcwd(), 已有默认参数
                      city="温州市",
                      cityCode="0577",
                      adCode="330304",
                      timeout=6,
                      nums=2
                      )
ttbike.run(120.689762, 27.917881, 120.720772, 27.937222)

"120.689762,27.917881 ,120.720772,27.937222"
