import requests
import socket
import requests.packages.urllib3.util.connection as urllib3_cn
from constants import TELEGRAM_API_KEY


def send_msg(text):
    API_KEY = TELEGRAM_API_KEY
    chat_id = "862187105"
    url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(API_KEY, chat_id, text)
    response = requests.get(url, timeout=1)
    return (response.json())


if __name__ == '__main__':
    resp = send_msg("probando probando, probando mi amor por tii")
    print(resp)

# curl "https://api.telegram.org/bot1838828131:AAFVEPOylQgqm3v-CGeyotcKKrDKI-FY8bk/sendMessage?chat_id=862187105&text=HI"
