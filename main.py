import requests
import selectorlib
import smtplib, ssl
import os
import time
import sqlite3

url = "http://programmer100.pythonanywhere.com/tours/"

connection = sqlite3.connect("eventsdata.db")


def scrape(url):
    response = requests.get(url)
    source = response.text
    return source


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)["tours"]
    return value

def send_email(message):
    host = "smtp.gmail.com"
    port = 465
    username = ""
    receiver = ""
    password = "pwactfcgtmvfjium"
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)
    print("email sent")


def store(extracted):
    row = extracted.split(",")
    row = [item.strip() for item in row]
    cursor = connection.cursor()
    cursor.execute("Insert into Events VALUES(?, ?, ?)", row)
    connection.commit()


def read(extracted):
    row = extracted.split(",")
    row = [item.strip() for item in row]
    cursor = connection.cursor()
    band_name, city, date = row
    cursor.execute("Select * from Events where band_name=? AND city=? AND date=?", (band_name, city, date))
    rows = cursor.fetchall()
    print(rows)
    return rows


if __name__ == "__main__":
    while True:
        scraped = scrape(url)
        extracted = extract(scraped)
        print(extracted)

        if extracted != "No upcoming tours":
            row = read(extracted)
            if not row:
                store(extracted)
                send_email(message=f"New Event was found Homie! Take a look it is, {extracted}")
        time.sleep(2)
