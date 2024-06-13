# importing library
from flask import Flask, jsonify, request
from selenium import webdriver
from time import sleep
import pandas as pd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Create app with Flask
app = Flask(__name__)


def scraper(url):  # scraper func
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # to hide browsers we have to open it because the site have captcha
    df = pd.DataFrame(columns=['marka', 'seri', 'model', 'ad_describe', 'year', 'km', 'price_tl', 'ad_date', 'adress'])
    webdriver_service = Service('C:/Program Files (x86)/chromedriver.exe')
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    driver.get(url)
    sleep(2)
    driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()  # accept cookies
    while True:
        try:  # scraping items by xpath method
            marka_items = driver.find_elements(By.XPATH, '//*[@id="searchResultsTable"]/tbody/tr[*]/td[2]')
            seri_items = driver.find_elements(By.XPATH, '//*[@id="searchResultsTable"]/tbody/tr[*]/td[3]')
            model_items = driver.find_elements(By.XPATH, '//*[@id="searchResultsTable"]/tbody/tr[*]/td[4]')
            ad_title_items = driver.find_elements(By.XPATH, '//*[@id="searchResultsTable"]/tbody/tr[*]/td[5]')
            year_items = driver.find_elements(By.XPATH, '//*[@id="searchResultsTable"]/tbody/tr[*]/td[6]')
            km_items = driver.find_elements(By.XPATH, '//*[@id="searchResultsTable"]/tbody/tr[*]/td[7]')
            price_items = driver.find_elements(By.XPATH, '//*[@id="searchResultsTable"]/tbody/tr[*]/td[8]')
            ad_date_items = driver.find_elements(By.XPATH, '//*[@id="searchResultsTable"]/tbody/tr[*]/td[9]')
            adress_items = driver.find_elements(By.XPATH, '//*[@id="searchResultsTable"]/tbody/tr[*]/td[10]')
            #  add the items to data frame
            for i in range(len(marka_items)):
                df.loc[len(df)] = [
                    marka_items[i].text, seri_items[i].text, model_items[i].text, ad_title_items[i].text,
                    year_items[i].text, km_items[i].text, price_items[i].text, ad_date_items[i].text,
                    adress_items[i].text
                ]

            next_button = driver.find_element(By.XPATH, '//*[@id="searchResultsSearchForm"]/div[1]/div[3]/div[3]/div[1]/ul/li[15]/a')
            next_button.click()
            sleep(2)
        except:
            break

    print(f'{len(df)} adverts founded')
    driver.quit()
    return df


def make_endpoint_url(user_filters, arguments, url):
    new_url = url
    if 'marka' in user_filters.keys():
        if user_filters['marka'].lower() in arguments['marka']:
            marka = user_filters['marka'].lower()
            new_url = f'https://www.sahibinden.com/{marka}'
    if 'fuel_type' in user_filters.keys():
        f = arguments['fuel_type'][user_filters['fuel_type']]
        new_url += f'/{f}'
    if 'gear' in user_filters.keys():
        g = arguments['gear'][user_filters['gear']]
        new_url += f'/{g}'
    if 'renk' in user_filters.keys():
        r = arguments['renk'][user_filters['renk']]
        new_url += f'/?a3={r}'
    if 'max_km' in user_filters.keys() and '?' in url:
        m_k = user_filters['max_km']
        new_url += f'/&a4_max={m_k}'
    if 'max_km' in user_filters.keys() and '?' not in url:
        m_k = user_filters['max_km']
        new_url += f'/?a4_max={m_k}'

    return url


def send_file_by_email(sender_email, recipient_email, sender_password, path_to_file, file_name):
    subject = "Advertisements you requested"
    body = """Hello, In the attachment you will find ads that fit your search criteria\nHappy day"""
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465

    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = recipient_email
    body_part = MIMEText(body)
    message.attach(body_part)

    try:
        with open(path_to_file,'rb') as file:
            message.attach(MIMEApplication(file.read(), Name=file_name))
    except:
        print('cant find any file to send')
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
           server.login(sender_email, sender_password)
           server.sendmail(sender_email, recipient_email, message.as_string())
    except:
        print('Please verify your password and email address')

    print("Has been sent")


@app.route('/scrape', methods=['POST'])
def start_scrape():
    url = 'https://www.sahibinden.com/otomobil'

    try:
        user_filter = request.json.get('filters', {})
        with open('filter_options.json') as filter_file:
            filter_dict = json.load(filter_file)

        url_filters = make_endpoint_url(user_filter, filter_dict, url)
        ads_df = scraper(url_filters)

        ads_df.to_excel('ads_file.xlsx')

        return jsonify({"status": "success", "message": "Scraping completed successfully!"}), 200

    except:
        return jsonify({"status": "error"}), 500


@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        user_mail = request.json.get('email', '')
        with open('email_info.json') as email_info:
            email_info_dict = json.load(email_info)

        file_name = 'ads_file.xlsx'
        send_file_by_email(email_info_dict['email'], user_mail, email_info_dict['password'], file_name, file_name)

        return jsonify({"status": "success", "message": "the email has been send successfully!"}), 200
    except:
        return jsonify({"status": "error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

