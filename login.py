from time import sleep
from selenium import webdriver


def login():
    driver = webdriver.Chrome()
    driver.implicitly_wait(4)
    driver.get("https://dubai.dubizzle.com")

    login_button = driver.find_element_by_xpath('//*[@id="page-wrapper"]/div[1]/div[2]/div[2]/div/div[2]/button[3]')
    login_button.click()

    email_button = driver.find_element_by_xpath('//*[@id="popup_login_link"]')
    email_button.click()

    email_field = driver.find_element_by_xpath('//*[@id="popup_email"]')
    email_field.clear()
    email_field.send_keys('amirhossein1234bonakdar@gmail.com')

    password_field = driver.find_element_by_xpath('//*[@id="popup_password"]')
    password_field.clear()
    password_field.send_keys('Salam0011')

    login_submit_button = driver.find_element_by_xpath('//*[@id="popup_login_btn"]')
    login_submit_button.click()

    sleep(7)

    driver.close()


if __name__ == "__main__":
    login()
