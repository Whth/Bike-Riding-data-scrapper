"""
    import requests
    header={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Ap"}
    tqwz="https://v0.yiketianqi.com/api?unescape=1&version=v91&appid=43656176&appsecret=I42og6Lm&ext=&cityid=101210701"
    re=requests.post(tqwz,headers=header)
    sdf=re.json()
    city=sdf["city"]
    update_time=sdf["update_time"]
    data=sdf["data"][0]
    wea=data["wea"]   #天气情况
    tem=data["tem"]   #天气温度
    tem1=data["tem1"] #天气最高温度
    tem2=data["tem2"] #天气最低温度
    humidity=data["humidity"]  #湿度
    print(city+"今日天气"+wea+","+"温度"+tem+","+"最高温度"+tem1+"最低温度"+tem2+"降水概率"+humidity)
"""
import requests


class WeatherCop_:

    def __init__(self, ):
        pass

    def weather(self):
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Ap"}
        tqwz = "https://v0.yiketianqi.com/api?unescape=1&version=v91&appid=43656176&appsecret=I42og6Lm&ext=&cityid=101210701"
        re = requests.post(tqwz, headers=header)
        sdf = re.json()
        city = sdf["city"]
        update_time = sdf["update_time"]
        data = sdf["data"][0]
        wea = data["wea"]  # 天气情况
        tem = data["tem"]  # 天气温度
        tem1 = data["tem1"]  # 天气最高温度
        tem2 = data["tem2"]  # 天气最低温度
        humidity = data["humidity"]  # 湿度
        print(
            city + "今日天气" + wea + "," + "温度" + tem + "," + "最高温度" + tem1 + "最低温度" + tem2 + "降水概率" + humidity)


if __name__ == '__main__':
    we = WeatherCop_()
    we.weather()
