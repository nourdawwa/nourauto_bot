from statistics import mean
import requests
from bs4 import BeautifulSoup
import telebot
from tabulate import tabulate
import inflect

# Initialize the inflect engine
p = inflect.engine()

# Initialize the Telebot with your bot token
bot = telebot.TeleBot("6294128281:AAFVLK4FH37_m27DxtREOTK8MHtCQTc45ro")


# Function to scrape the marks from the website
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


# Handle the /marks command
@bot.message_handler(commands=['marks'])
def send_marks(message):
    grades_data = scrape_marks()
    # message_text = ""
    # for subject_name, grade, term in grades_data:
    #     message_text += f"{subject_name} | {grade} | {term} \n"
    # headers = ['Course', 'Grade', 'Semester']
    #  headers=headers,

    table = tabulate(grades_data, tablefmt="pretty")
    bot.send_message(message.chat.id, table, parse_mode="Markdown")


# Handle the /last command
@bot.message_handler(commands=['last'])
def send_marks(message):
    grades_data = scrape_marks()
    last_term = grades_data[-1][2]
    # Filter the grades data to include only the grades with the same term as the last marks
    filtered_grades = [data for data in grades_data if (data[2] == last_term)]

    table = tabulate(filtered_grades, tablefmt="pretty")
    bot.send_message(message.chat.id, table, parse_mode="Markdown")


# Handle the /marks command
@bot.message_handler(commands=['count'])
def send_marks(message):
    grades_data = scrape_marks()
    total_marks_released = str(len(grades_data))

    bot.send_message(message.chat.id, total_marks_released, parse_mode="Markdown")


# Handle the /check4new command
@bot.message_handler(commands=['check4new'])
def send_marks(message):
    grades_data = scrape_marks()
    last_count = 22
    total_marks_released = len(grades_data)
    if total_marks_released > last_count:
        text_number = p.number_to_words(total_marks_released - last_count)
        text = f"there is {text_number} new grade{'s' if (total_marks_released - last_count) != 1 else ''}"
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
        cut_number = (total_marks_released - last_count) * -1
        new_grades = grades_data[cut_number:]
        table = tabulate(new_grades, tablefmt="pretty")
        bot.send_message(message.chat.id, table, parse_mode="Markdown")

    else:
        bot.send_message(message.chat.id, "Nothing New", parse_mode="Markdown")


# Handle the /last_mean command
@bot.message_handler(commands=['last_mean'])
def send_marks(message):
    grades_data = scrape_marks()
    last_term = grades_data[-1][2]
    total_marks_released = str(len(grades_data))
    filtered_grades = [float(data[1]) for data in grades_data if (data[2] == last_term) and float(data[1]) >= 60]
    mean_grade = str(round(mean(filtered_grades), 2))
    bot.send_message(message.chat.id, mean_grade, parse_mode="Markdown")


# Polling method to keep the bot running
bot.polling()
