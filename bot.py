import os
import requests
import logging
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from requests.exceptions import RequestException
import asyncio

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DEFAULT_LOCATION = os.getenv("LOCATION")  # Default city for weather

# Configure logging with timestamp
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Function to get weather data
async def get_weather(city):
    try:
        logging.info(f"Fetching weather for {city}...")
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses
        data = response.json()

        if data.get("cod") != 200:
            logging.warning(f"Weather fetch failed for {city}. Error: {data.get('message')}")
            return f"Unable to fetch weather for {city}. Please check the city name and try again."

        weather = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]

        weather_info = {
            "description": weather,
            "temperature": temp,
            "humidity": humidity
        }
        logging.info(f"Weather data for {city}: {weather_info}")
        return weather_info
    except RequestException as e:
        logging.error(f"Request error: {e}")
        return "Unable to fetch weather due to a network issue. Please try again later."
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return "An unexpected error occurred. Please try again later."

# Function to create a weather graph
def create_weather_graph(city, weather_data):
    labels = ["Temperature", "Humidity"]
    values = [weather_data["temperature"], weather_data["humidity"]]

    plt.figure(figsize=(8, 6))
    plt.bar(labels, values, color=['skyblue', 'lightgreen'])
    plt.title(f"Weather in {city}")
    plt.ylabel("Values")
    plt.savefig("weather.png")
    plt.close()

# Command to display weather
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = " ".join(context.args) if context.args else DEFAULT_LOCATION
    weather_data = await get_weather(city)

    if not weather_data or isinstance(weather_data, str):  # Error message is returned as string
        await update.message.reply_text(weather_data)
        return

    # Create and send weather graph
    create_weather_graph(city, weather_data)
    with open("weather.png", "rb") as photo:
        await context.bot.send_photo(chat_id=update.message.chat_id, photo=photo)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"User {update.message.chat.id} started the bot.")
    intro_text = (
        "Hello! I am WeatherBot, your personal weather assistant.\n"
        "I can provide you with the current weather and a graphical representation of the temperature and humidity.\n\n"
        "You can use the following command to interact with me:\n"
        "- `/weather [city name]`: Get the weather for any city and see a graphical representation."
    )
    await update.message.reply_text(intro_text)

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"User {update.message.chat.id} requested help.")
    help_text = (
        "Need help? Here are the commands you can use:\n"
        "- `/start`: Start the bot and get an introduction.\n"
        "- `/weather [city name]`: Get the weather for any city and see a graphical representation.\n"
        "- `/help`: Display this help message.\n"
        "- `/menu`: Display all available commands."
    )
    await update.message.reply_text(help_text)

# Menu command
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"User {update.message.chat.id} requested the menu.")
    menu_text = (
        "Here are all the available commands:\n"
        "- `/start`: Start the bot and get an introduction.\n"
        "- `/weather [city name]`: Get the weather for any city and see a graphical representation.\n"
        "- `/help`: Display help information.\n"
        "- `/menu`: Display all available commands."
    )
    await update.message.reply_text(menu_text)

# Main function to run the bot
async def main():
    # Initialize the Application
    app = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu))

    # Register bot commands
    await app.bot.set_my_commands([
        ("start", "Start the bot and get an introduction"),
        ("weather", "Get the weather for any city and see a graphical representation"),
        ("help", "Display help information"),
        ("menu", "Display all available commands")
    ])

    # Start polling
    logging.info("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
