from playwright.sync_api import sync_playwright
import re
import json
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


folder_path = Path("class data")

class_profiles = {
    "subject": ["HON", "PHY"],
    "catalog_number": [171, 121],
    "term": 2267,
    "class_number": [85327, 62630],
}

user_profiles = {
    "user": ["gene", "james"],
    "email": ["geneabeany@gmail.com", "jameshlim12@gmail.com"],
    "classes":  [[85327, 62630], [62630]]
}


def save_seats_data(count: int):
    file_path = folder_path / (class_profiles["subject"][count] + str(class_profiles["catalog_number"][count]) + ',' + str(class_profiles["class_number"][count]) + ".json")

    with open(file_path, "w") as f:
        json.dump(get_open_seats(count), f, indent=4)


def open_seats_data(count: int):
    file_path = folder_path / (class_profiles["subject"][count] + str(class_profiles["catalog_number"][count]) + ',' + str(class_profiles["class_number"][count]) + ".json")

    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        get_open_seats(count)


def get_open_seats(count: int):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(f"https://catalog.apps.asu.edu/catalog/classes/classlist?campusOrOnlineSelection=A&honors=F&keywords={class_profiles["class_number"][count]}&promod=F&searchType=all&term=2267")
        page.wait_for_load_state("networkidle")
        seats = int(re.search(r'\d+', page.inner_text(f"#class-results > div > div.focus.class-accordion.odd > div.class-results-cell.seats > div")).group())
        browser.close()
    return seats


def check():
    cp = class_profiles
    up = user_profiles
    noclasses = len(cp["subject"])

    for i in range(noclasses):
        try:
            last_seats = open_seats_data(i)
            current_seats = get_open_seats(i)
            if (last_seats != current_seats and last_seats is not None):
                print(cp["subject"][i] + str(cp["catalog_number"][i]) + ',' + str(cp["class_number"][i]) + ",previous: " + str(last_seats) + " current: " + str(current_seats))
                if (cp["class_number"][i] == 85327 and current_seats > 0):
                    swap_class()
                for j in range(len(up["classes"])):
                        if (cp["class_number"][i] == up["classes"][j][k]):
                            print(up["user"][j])
                            send_email(cp["subject"][i] + str(cp["catalog_number"][i]) + ',' + str(cp["class_number"][i]) + ",previous: " + str(last_seats) + " current: " + str(current_seats), up["user"][j])
                save_seats_data(i)
            else:
                print(cp["subject"][i] + str(cp["catalog_number"][i]) + ',' + str(cp["class_number"][i]) + ',' + "no change")
        except FileNotFoundError:
             last_seats = get_open_seats(i)
             save_seats_data(i)


def swap_class():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()
        page.goto("https://weblogin.asu.edu/cas/login?service=https%3A%2F%2Fweblogin.asu.edu%2Fcgi-bin%2Fcas-login%3Fcallapp%3Dhttps%253A%252F%252Fwebapp4.asu.edu%252Fmyasu%252F%253Finit%253Dfalse")
        page.wait_for_load_state("networkidle")
        page.locator("#username").fill("gyoon12")
        page.locator("#password").fill("Gegvismo*8")
        page.get_by_role("button", name = "Sign In", exact = True).click()


        page.get_by_role("link", name = "Registration").click()
        page.get_by_role("link", name = "Swap").click()
        page.locator("#DERIVED_REGFRM1_DESCR50\\$4\\$").select_option("HON 171: The Human Event I (85315)")
        page.locator("#DERIVED_REGFRM1_CLASS_NBR").fill("85327")
        page.locator("#SSR_SWAP_FL_WRK_SSR_PB_SRCH").click()
        page.locator("#PT_NEXT").click()
        page.locator("#DERIVED_SSR_FL_SSR_SELECT").click()
        page.locator("#SSR_ENRL_FL_WRK_SUBMIT_PB").click()
        page.locator("#\\#ICYes").click()
        

def send_email(message: str, user: str):
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


def create_folder():
    folder_path.mkdir(parents=True, exist_ok=True)




create_folder()
check()