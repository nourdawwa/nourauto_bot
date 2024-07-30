import time
from statistics import mean
import requests
from bs4 import BeautifulSoup
import telebot
from tabulate import tabulate
import inflect
import threading
import os
# Initialize the inflect engine
p = inflect.engine()
# Initialize the Telebot with your bot token
my_secret = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(my_secret)

allowed_chat_ids = [903999664, ]

def scrape_marks():
    url = "http://app.hama-univ.edu.sy/StdMark/Student/821080713?college=1"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all <tr> elements with class "bg-light" to extract grades data
    grades_data = []
    for tr in soup.find_all('tr', class_='bg-light'):
        td_elements = tr.find_all('td')
        subject_name = td_elements[0].get_text(strip=True)
        grade = td_elements[2].get_text(strip=True)
        term = td_elements[1].get_text(strip=True)
        grades_data.append((subject_name, grade, term))

    return grades_data


# Function to read the number from the file
def read_number_from_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            number = int(file.read())
        return number
    else:
        return None


# Function to write the number to the file
def write_number_to_file(file_path, number):
    with open(file_path, 'w') as file:
        file.write(str(number))


# Function to scrape the marks from the website
@bot.message_handler(commands=['marks'])
def send_marks(message):
    chat_id = message.chat.id
    grades_data = scrape_marks()
    table = tabulate(grades_data, tablefmt="pretty")
    if chat_id in allowed_chat_ids:
        bot.send_message(message.chat.id, table, parse_mode="Markdown")
    else:
        with open('foff.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video)


# Handle the /last command
@bot.message_handler(commands=['last'])
def send_marks(message):
    chat_id = message.chat.id
    grades_data = scrape_marks()
    last_term = grades_data[-1][2]
    # Filter the grades data to include only the grades with the same term as the last marks
    filtered_grades = [data for data in grades_data if (data[2] == last_term)]

    table = tabulate(filtered_grades, tablefmt="pretty")
    if chat_id in allowed_chat_ids:
    bot.send_message(message.chat.id, table, parse_mode="Markdown")
    else:
        with open('foff.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video)


# Handle the /count command
@bot.message_handler(commands=['count'])
def send_marks(message):
    chat_id = message.chat.id
    grades_data = scrape_marks()
    total_marks_released = str(len(grades_data))
    write_number_to_file('lastChecked.txt', total_marks_released)

    if chat_id in allowed_chat_ids:
    bot.send_message(message.chat.id, total_marks_released, parse_mode="Markdown")
    else:
        with open('foff.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video)

# Handle the /check4new command
@bot.message_handler(commands=['check4new'])
def send_marks(message):
    chat_id = message.chat.id
    grades_data = scrape_marks()
    last_count = read_number_from_file('lastChecked.txt')
    total_marks_released = len(grades_data)

    if chat_id in allowed_chat_ids:
        if total_marks_released > last_count:
            text_number = p.number_to_words(total_marks_released - last_count)
            text = f"there is {text_number} new grade{'s' if (total_marks_released - last_count) != 1 else ''}"
            bot.send_message(message.chat.id, text, parse_mode="Markdown")
            cut_number = (total_marks_released - last_count) * -1
            new_grades = grades_data[cut_number:]
            table = tabulate(new_grades, tablefmt="pretty")
            bot.send_message(message.chat.id, table, parse_mode="Markdown")
            write_number_to_file('lastChecked.txt', total_marks_released)
        else:
            bot.send_message(message.chat.id, "Nothing New", parse_mode="Markdown")
    else:
        with open('foff.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video)
    


# Handle the /last_mean command
@bot.message_handler(commands=['last_mean'])
def send_marks(message):
    chat_id = message.chat.id
    grades_data = scrape_marks()
    last_term = grades_data[-1][2]
    total_marks_released = str(len(grades_data))
    filtered_grades = [float(data[1]) for data in grades_data if (data[2] == last_term) and float(data[1]) >= 60]
    mean_grade = str(round(mean(filtered_grades), 2))
    if chat_id in allowed_chat_ids:
        bot.send_message(message.chat.id, mean_grade, parse_mode="Markdown")
    else:
        with open('foff.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video)


# Handle the /myid command
@bot.message_handler(commands=['myid'])
def get_user_id(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, f"Your User ID is: {user_id}")


def check_for_marks():
    last_checked = read_number_from_file('lastChecked.txt')
    print("last checked", last_checked)
    user_id = "903999664"
    grades_data = scrape_marks()
    new_check = len(grades_data)
    if new_check > last_checked:
        text_number = p.number_to_words(new_check - last_checked)
        text = f"there is {text_number} new grade{'s' if (new_check - last_checked) != 1 else ''}"
        bot.send_message(user_id, text, parse_mode="Markdown")
        cut_number = (new_check - last_checked) * -1
        new_grades = grades_data[cut_number:]
        table = tabulate(new_grades, tablefmt="pretty")
        bot.send_message(user_id, table, parse_mode="Markdown")


def bot_polling():
    bot.polling()


bot_thread = threading.Thread(target=bot_polling)
bot_thread.start()

while True:
    check_for_marks()
    time.sleep(5 * 60)

