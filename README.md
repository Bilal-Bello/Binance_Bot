# Binance BTC Exposure Bot

A simple Python trading bot that keeps BTC exposure below a defined cap by converting excess BTC to USDT automatically.

## Features

- Binance Spot API integration
- Secure API key handling via environment variables
- Exposure control strategy
- Runs continuously on a VPS

## Requirements

- Python 3.9+
- Binance account with API access

## Installation

Clone the repository:

git clone https://github.com/yourusername/binance-trading-bot.git

Navigate to the project folder:

cd binance-trading-bot

Create a virtual environment:

python3 -m venv venv
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

## Configuration

Copy the example config file:

cp config_example.env .env

Edit the file and add your API keys:

BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret

## Run the bot

python bot.py

## Warning

This software is for educational purposes only.
Trading cryptocurrencies carries financial risk.
