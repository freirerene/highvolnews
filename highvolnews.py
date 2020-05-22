import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd
from datetime import date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.headerregistry import Address
from tabulate import tabulate


urlheader = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36", "X-Requested-With": "XMLHttpRequest"}

class Scraper:
    def __init__(self):
        self.markup = requests.get('https://www.investing.com/economic-calendar/', headers=urlheader).text


    def parse(self):
        soup = BeautifulSoup(self.markup, 'html.parser')
        events = soup.find_all("tr", {"class": "js-event-item"})

        list_events = []

        for i in range(0,len(events)-1):
        	list_events.append([events[i].get("data-event-datetime"), events[i].next_element.next_element.next_element.next_element.next_element.next_element.get("title"), events[i].next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.get("title"), events[i].a.text[12:]])

        self.pd_events = pd.DataFrame(list_events)

        high = self.pd_events[self.pd_events[2] == 'High Volatility Expected']
        high.reset_index()
        high[0] = pd.to_datetime(high[0])
        high[0] = high[0].dt.tz_localize('America/New_York')
        high[0] = high[0].dt.tz_convert('America/Sao_Paulo')
        high[1] = high[1]
        high_us = high[high[1] == 'United States']
        high_br = high[high[1] == 'Brazil']
        high_us.reset_index()
        high_br.reset_index()

        self.noticias = pd.concat([high_us, high_br])
        

    def sendemail(self):
        fromEmail = "from@email.com"
        toEmail = "to@email.com"

        today = date.today()

        d2 = today.strftime("%d %B, %Y")

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Digest for %s" % (d2)
        msg["From"] = fromEmail
        msg["To"] = toEmail

        text = """
        Eventos do dia: <br>
        <br>

        %s 
        <br>

        """ % (tabulate(self.noticias, tablefmt="html", showindex="never", headers=["Data","Pais", "Vol", "Evento"]))

        mime = MIMEText(text, 'html')

        msg.attach(mime)

        try:
            mail = smtplib.SMTP('smtp.gmail.com', 587)
            mail.ehlo()
            mail.starttls()
            mail.login(fromEmail, 'password')
            mail.sendmail(fromEmail, toEmail, msg.as_string())
            mail.quit()
            print('Email sent!')
        except Exception as e:
            print('Something went wrong... %s' % e)

        
 

s = Scraper()
s.parse()
s.sendemail()
