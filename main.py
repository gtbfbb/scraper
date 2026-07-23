from playwright.sync_api import sync_playwright
import re
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class_profiles = {
    "subject": ["HON", "PHY", "PHY", "PHY", "PHY", "PHY", "PHY"],
    "catalog_number": [171, 122, 122, 122, 122, 122, 121],
    "term": 2267,
    "class_number": [85327, 64179, 61035, 64566, 68728, 70263, 62630],
}


user_profiles = {
    "user": ["gene", "james"],
    "email": ["geneabeany@gmail.com", "jameshlim12@gmail.com"],
    "classes":  [[85327, 64179, 61035, 64566, 68728, 70263], [62630]]
}


def save_seats(class_profiles, count: int):
    with open(class_profiles["subject"][count] + str(class_profiles["catalog_number"][count]) + ',' + str(class_profiles["class_number"][count]) + ".json", "w") as f:
            json.dump(get_open_seats(class_profiles, count), f, indent=4)


def open_seats(class_profiles, count: int):
    try:
        with open(class_profiles["subject"][count] + str(class_profiles["catalog_number"][count]) + ',' + str(class_profiles["class_number"][count]) + ".json", "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        get_open_seats(class_profiles, count)
    

def get_open_seats(class_profiles, count: int):
    with sync_playwright() as p:
        browser = p.webkit.launch() 
        page = browser.new_page()
        page.goto(f"https://catalog.apps.asu.edu/catalog/classes/classlist?campusOrOnlineSelection=A&honors=F&keywords={class_profiles["class_number"][count]}&promod=F&searchType=all&term=2267")
        page.wait_for_load_state("networkidle")
        seats = int(re.search(r'\d+', page.inner_text(f"#class-results > div > div.focus.class-accordion.odd > div.class-results-cell.seats > div")).group())
        browser.close()
    return seats


def check():
    global class_profiles
    global user_profiles
    cp = class_profiles
    up = user_profiles
    noclasses = len(cp["subject"])
    nousers = len(up["user"])


    for i in range(noclasses):
        try:
            last_seats = open_seats(cp, i)
            current_seats = get_open_seats(cp, i)
            if (last_seats != current_seats and last_seats is not None):
                print(cp["subject"][i] + str(cp["catalog_number"][i]) + ',' + str(cp["class_number"][i]) + ",previous: " + str(last_seats) + " current: " + str(current_seats))
                for j in range(len(up["classes"])):
                    for k in range(len(up["classes"][j])):
                        if (cp["class_number"][i] == up["classes"][j][k]):
                            print(up["user"][j])
                            send_email(cp["subject"][i] + str(cp["catalog_number"][i]) + ',' + str(cp["class_number"][i]) + ",previous: " + str(last_seats) + " current: " + str(current_seats), up["user"][j])
            else:
                 print(cp["subject"][i] + str(cp["catalog_number"][i]) + ',' + str(cp["class_number"][i]) + ',' + "no change")
        except FileNotFoundError:
             last_seats = get_open_seats
        save_seats(cp, i)
    

def send_email(message: str, user: str):
    global user_profiles
    up = user_profiles
    user_pos = up["user"].index(user)

    sender_email = "geneabeany@gmail.com"
    receiver_email = up["email"][user_pos]
    password = "lyiq qqjw egxm ukkt" 

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = ""

    body = message
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())


check()