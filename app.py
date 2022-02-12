from selenium import webdriver
import time
import os
from flask import Flask, request
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import telebot
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from img_to_text import get_text_from_img
from deep_translator import GoogleTranslator

TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)
DRIVER = None
URL = 'https://quizlet.com/'
DESCRIPTION_LINK = 'https://telegra.ph/Quizlet-Sets-Generator-01-25'

opened = False
logged = False
set_created = False
photo_processed = False
login = ''
title = ''
tlang = ''
dlang = ''
words_list = []
photo_words = []


server = Flask(__name__)


def open_browser():
    options = webdriver.ChromeOptions()
    options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-sh-usage')
    options.add_argument('--window-size=1300,1000')
    options.add_experimental_option('detach', True)
    global DRIVER
    DRIVER = webdriver.Chrome(executable_path=os.environ.get('CHROMEDRIVER_PATH'), chrome_options=options)
    DRIVER.get(URL)
    DRIVER.find_element(By.CLASS_NAME, 'SiteNavLoginSection-loginButton').click()


def login_browser(login, password):
    login_input = DRIVER.find_element(By.ID, 'username')
    DRIVER.find_element(By.ID, 'username').clear()
    login_input.send_keys(login)
    password_input = DRIVER.find_element(By.ID, 'password')
    DRIVER.find_element(By.ID, 'password').clear()
    password_input.send_keys(password)
    DRIVER.find_element(By.CLASS_NAME, 'UILoadingButton').click()
    time.sleep(1)
    try:
        DRIVER.find_element(By.CLASS_NAME, 'SiteNavLoginSection-loginButton')
    except:
        return True
    return False


def logout_browser():
    click_me = DRIVER.find_element(By.CLASS_NAME, 'SiteAvatar')
    click_me.click()
    action = ActionChains(DRIVER)
    action.move_to_element(click_me).move_by_offset(-130, 550).click().perform()


def create_set_browser():
    click_me = DRIVER.find_element_by_xpath("//*[@aria-label='Create']")
    click_me.click()
    action = ActionChains(DRIVER)
    action.move_to_element(click_me).move_by_offset(0, 40).click().perform()
    try:
        DRIVER.find_element(By.CLASS_NAME, 'ckk0ebs').click()
    except:
        pass


def set_params_browser():
    global tlang, dlang
    name_field = DRIVER.find_element_by_xpath("//*[@class='AutoExpandTextarea-textarea'][@maxlength='255']")
    DRIVER.find_element_by_xpath("//*[@class='AutoExpandTextarea-textarea'][@maxlength='255']").clear()
    name_field.send_keys(title)
    DRIVER.find_element_by_xpath("//*[@data-testid='PMEditor']").click()
    DRIVER.find_element_by_xpath("//*[text()='CHOOSE LANGUAGE']").click()
    term_lang_field = DRIVER.find_element_by_xpath("//*[@placeholder='Search languages']")
    term_lang_field.send_keys(tlang)
    action = ActionChains(DRIVER)
    tlang = DRIVER.find_element_by_xpath("//*[@class='LanguageSelect-option']").text
    term_lang_field.send_keys(Keys.ENTER)
    time.sleep(1)
    DRIVER.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
    time.sleep(1)
    DRIVER.find_element_by_xpath("//*[text()='CHOOSE LANGUAGE']").click()
    definition_lang_field = DRIVER.find_element_by_xpath("//input[@aria-owns='react-select-3--list']")
    definition_lang_field.send_keys(dlang)
    dlang = DRIVER.find_element_by_xpath("//*[@class='LanguageSelect-option']").text
    definition_lang_field.send_keys(Keys.ENTER)


def fill_set_browser():
    DRIVER.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
    for word in words_list:
        add_word_browser(word)
        time.sleep(0.05)
    DRIVER.find_element_by_xpath("//*[@class='CreateSetHeader-infoButtonWrap']").click()
    wait = WebDriverWait(DRIVER, 10)
    wait.until(EC.visibility_of_element_located((By.XPATH, "//button[@class='UIButton UIButton--inverted']"))).click()
    time.sleep(1.5)
    try:
        DRIVER.find_element(By.CLASS_NAME, 'ckk0ebs').click()
    except:
        pass


def add_word_browser(word):
    try:
        term_field = DRIVER.find_element_by_xpath(f"//div[@aria-placeholder='Enter {tlang}']")
    except:
        DRIVER.find_element_by_xpath("//*[@aria-label='+ Add card']").click()
        term_field = DRIVER.find_element_by_xpath(f"//div[@aria-placeholder='Enter {tlang}']")
    term_field.send_keys(word)
    definition_field = DRIVER.find_element_by_xpath(f"//div[@aria-placeholder='Enter {dlang}']")
    translated_word = GoogleTranslator(source=tlang.lower(), target=dlang.lower()).translate(word)
    definition_field.send_keys(translated_word)


@bot.message_handler(commands=['start'])
def start(message):
    global opened
    opened = False
    global logged
    logged = False
    global set_created
    set_created = False
    bot.send_message(message.chat.id, 'Welcome 😄\n\n'
                                      'See /help for a list of commands.\n\n'
                                      f'Click {DESCRIPTION_LINK} to get more detailed info about how to use this bot.')


@bot.message_handler(commands=['help'])
def help_commands(message):
    bot.send_message(message.chat.id, '𝐋𝐢𝐬𝐭 𝐨𝐟 𝐚𝐥𝐥 𝐛𝐨𝐭 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬:\n'
                                      '/login - command to log in to an account\n'
                                      '/create_set - command to create a new set\n'
                                      '/submit_set - command to save a new set\n'
                                      '/logout - command to logout from an account\n')


@bot.message_handler(commands=['login'])
def login(message):
    global logged
    if not logged:
        bot.send_message(message.chat.id, 'To input the credentials of your Quizlet account, '
                                          'format of the message must be:\n\n'
                                          '\'newuser\'  -  login\n'
                                          '\'********\' -  password\n')
        input_credentials(message)
    else:
        bot.send_message(message.chat.id, 'You are already logged in. If you want to change account, send /logout and '
                                          'then /login.')


def input_credentials(message):
    bot.register_next_step_handler(message, fill_credentials)


def fill_credentials(message):
    credentials = message.text
    global login
    login, password = credentials.split('\n')
    bot.send_message(message.chat.id, f'Logging in, please wait...\n'
                                      f'It can take about 1 min...')
    global opened
    if not opened:
        open_browser()
        opened = True
    if login_browser(login, password):
        bot.send_message(message.chat.id, f'Successfully logged in to \'{login}\' Quizlet account.')
        global logged
        logged = True
    else:
        bot.send_message(message.chat.id, f'The login details you entered are incorrect. Try again...')
        input_credentials(message)


@bot.message_handler(commands=['logout'])
def logout(message):
    global logged
    if logged:
        DRIVER.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
        bot.send_message(message.chat.id, f'Logging out, please wait...')
        time.sleep(1)
        logout_browser()
        logged = False
        global login
        bot.send_message(message.chat.id, f'Successfully logged out from \'{login}\' Quizlet account.')
        login = None
        global opened
        opened = False
        DRIVER.quit()
    else:
        bot.send_message(message.chat.id, f'Cannot log out because you are not logged in.')


@bot.message_handler(commands=['create_set'])
def create_set(message):
    if logged:
        global words_list
        words_list = []
        bot.send_message(message.chat.id, 'Creating a set, please wait...')
        create_set_browser()
        bot.send_message(message.chat.id, 'Input name of a new set:')
        bot.register_next_step_handler(message, get_set_name)
    else:
        bot.send_message(message.chat.id, 'Cannot create a set because you are not logged.')


def get_set_name(message):
    if message.text.find('/') == -1:
        global title
        title = message.text
        bot.send_message(message.chat.id, 'Input term language:')
        bot.register_next_step_handler(message, get_term_lang)
    elif message.text.find('/logout') != -1:
        logout(message)
    else:
        bot.send_message(message.chat.id, 'Wrong set name.')
        bot.send_message(message.chat.id, 'Input name of a new set:')
        bot.register_next_step_handler(message, get_set_name)


def get_term_lang(message):
    if message.text.find('/') == -1:
        global tlang
        tlang = message.text
        bot.send_message(message.chat.id, 'Input definition language:')
        bot.register_next_step_handler(message, get_definition_lang)
    elif message.text.find('/logout') != -1:
        logout(message)
    else:
        bot.send_message(message.chat.id, 'Wrong term language.')
        bot.send_message(message.chat.id, 'Input term language:')
        bot.register_next_step_handler(message, get_term_lang)


def get_definition_lang(message):
    if message.text.find('/') == -1:
        global dlang
        dlang = message.text
        bot.send_message(message.chat.id, 'Changing settings...')
        set_params_browser()
        bot.send_message(message.chat.id, 'Now you can send unknown words (photo or text format).\n'
                                          'Send /submit_set when you want to stop.')
        global set_created
        set_created = True
    elif message.text.find('/logout') != -1:
        logout(message)
    else:
        bot.send_message(message.chat.id, 'Wrong definition language.')
        bot.send_message(message.chat.id, 'Input definition language:')
        bot.register_next_step_handler(message, get_definition_lang)


@bot.message_handler(content_types=['text'])
def fill_set(message):
    if logged and set_created and not photo_processed:
        if message.text == '/submit_set':
            submit_set(message)
        elif message.text == '/confirm_words':
            words_list.extend(photo_words)
            bot.send_message(message.chat.id, 'Successfully confirmed.\n'
                                              'You can continue sending unknown words (photo or text format).')
        else:
            words = message.text.split('\n')
            words_list.extend(words)


def process_photo(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    img = bot.download_file(file_info.file_path)
    global photo_words
    photo_words = get_text_from_img(img, tlang)


@bot.message_handler(content_types=['photo'])
def fill_photo_words(message):
    global photo_processed
    if logged and set_created and not photo_processed:
        photo_processed = True
        bot.send_message(message.chat.id, 'Processing the photo...')
        process_photo(message)
        bot.send_message(message.chat.id, '𝐅𝐨𝐮𝐧𝐝 𝐰𝐨𝐫𝐝𝐬:\n' + '\n'.join(photo_words))
        bot.send_message(message.chat.id, 'If everything is recognized right, send /confirm_words.\n'
                                          'Otherwise, edit the received message and send it again.')
        photo_processed = False


def submit_set(message):
    if logged:
        if '\n'.join(words_list).count('\n') < 1:
            bot.send_message(message.chat.id, 'Cannot submit the set because there are fewer than two unknown words.\n'
                                              'Add at least one another word and then send /submit_set.')
        else:
            joined_wl = '\n'.join(words_list)
            bot.send_message(message.chat.id, f'𝐋𝐢𝐬𝐭 𝐨𝐟 𝐰𝐨𝐫𝐝𝐬 𝐭𝐡𝐚𝐭 𝐰𝐢𝐥𝐥 𝐛𝐞 𝐚𝐝𝐝𝐞𝐝 𝐭𝐨 𝐭𝐡𝐞 \'{title}\' 𝐬𝐞𝐭:\n' + joined_wl)
            bot.send_message(message.chat.id, 'Submitting...')
            fill_set_browser()
            global set_created
            set_created = False
            bot.send_message(message.chat.id, 'Sucessfully created the set.')
    else:
        bot.send_message(message.chat.id, 'Cannot submit a set because you are not logged in.')


@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def web_hook():
    bot.remove_webhook()
    bot.set_webhook(url=os.getenv('HEROKU_URL') + TOKEN)
    return "!", 200


bot.infinity_polling()


if __name__ == "__main__":
    server.run(host='0.0.0.0', port=os.environ.get('PORT', '5000'))

