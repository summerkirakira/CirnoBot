from pydantic import BaseSettings


class Config(BaseSettings):

    class Config:
        extra = "ignore"
        trans_lib = {
            "人民币": "CNY",
            "美元": "USD",
            "美金": "USD",
            "美刀": "USD",
            "韩国元": "KRW",
            "韩元": "KRW",
            "新台币": "TWD",
            "日元": "JPY",
            "澳大利亚元": "AUD",
            "澳币": "AUD",
            "英镑": "GBP",
            "印尼卢比": "IDR",
            "新西兰元": "NZD",
            "新加坡元": "SGD",
            "泰国铢": "THB",
            "瑞典克朗": "SEK",
            "瑞士法郎": "CHF",
            "卢布": "RUB",
            "菲律宾比索": "PHP",
            "港币": "HKD",
            "林吉特": "MYR",
            "欧元": "EUR",
            "印度卢比": "INR",
            "卢比": "INR",
            "丹麦克朗": "DKK",
            "加拿大元": "CAD",
            "挪威克朗": "NOK",
            "阿联酋迪拉姆": "AED",
            "沙特里亚尔": "SAR",
            "巴西里亚尔": "BRL",
            "澳门元": "MOP",
            "澳元": "MOP",
            "南非兰特": "ZAR",
            "土耳其里拉": "TRY",
        }