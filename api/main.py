from datetime import datetime, timedelta
import calendar

import requests
import uvicorn
from fastapi import FastAPI


app = FastAPI()


@app.get("/national_bank/{currency}/{date}")
async def national_bank(currency: str, date: str):
    if currency == "USD":
        currency = 431
    elif currency == "EUR":
        currency = 451
    elif currency == "GBP":
        currency = 429
    elif currency == "JPY":
        currency = 508

    response = None

    if date != "0":
        request = requests.get(
            f"https://api.nbrb.by/exrates/rates/{currency}?ondate={date}"
        )
        response = request.json()
        return {"exchange": f"{response['Cur_OfficialRate']}"}
    elif date == "0":
        request = requests.get(f"https://api.nbrb.by/exrates/rates/{currency}")
        response = request.json()
        return {"exchange": f"{response['Cur_OfficialRate']}"}


@app.get("/belarus_bank/{currency}/{date}")
async def belarus_bank(currency: str, date: str):
    request = requests.get("https://belarusbank.by/api/kurs_cards")
    response = request.json()

    selected_currency_rates = []

    for entry in response:
        if (
            entry["kurs_date_time"].startswith(date)
            and currency.upper() + "CARD_in" in entry
        ):
            selected_currency_rates.append(
                {
                    "kurs_date_time": entry["kurs_date_time"],
                    f"{currency.upper()}CARD_in": entry[f"{currency.upper()}CARD_in"],
                    f"{currency.upper()}CARD_out": entry[f"{currency.upper()}CARD_out"],
                }
            )
            break

    if selected_currency_rates is not None:
        return selected_currency_rates
    else:
        return {"message": f"No data available for {currency} on {date}"}


@app.get("/alfabank/{currency}")
async def alfabank(currency: str):

    request = requests.get(
        f"https://developerhub.alfabank.by:8273/partner/1.0.1/public/rates"
    )
    response = request.json()

    for rate in response["rates"]:
        if rate["sellIso"] == currency and rate["buyIso"] == "BYN":
            return {"sellRate": f"{rate['sellRate']}", "buyRate": f"{rate['buyRate']}"}
    return {"Error": "Нету такой валюты"}

@app.get("/statistic/{currency}")
async def statistic(currency: str):
    if currency == "USD":
        currency = 431
    elif currency == "EUR":
        currency = 451
    elif currency == "GBP":
        currency = 429
    elif currency == "JPY":
        currency = 508
    today = datetime.now()
    one_month_ago = today - timedelta(days=calendar.monthrange(today.year, today.month-1)[1])

    today_formatted = today.strftime("%m-%d-%Y")
    one_month_ago_formatted = one_month_ago.strftime("%m-%d-%Y")
    
    request = requests.get(f"https://api.nbrb.by/exrates/rates/dynamics/{currency}?startdate={one_month_ago_formatted}&enddate={today_formatted}")
    response = request.json()
    cur_officialrate_list = []

    for item in response:
        cur_officialrate_list.append(item['Cur_OfficialRate'])
    result = {
        "cur_officialrate_list": cur_officialrate_list,
        "one_month_ago_formatted": one_month_ago_formatted,
        "today_formatted": today_formatted
    }
    return result


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)
