#%%
import requests
import json
import pandas as pd
import yfinance as yf
#%%
url = 'https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/czbh/mm23/data'

header = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}

r = requests.get(url, headers=header)
# https://stackoverflow.com/questions/43590153/http-error-403-forbidden-when-reading-html
data = json.loads(r.text)
rpi_yronyr_df = pd.json_normalize(data, record_path=['months'])
#https://towardsdatascience.com/how-to-convert-json-into-a-pandas-dataframe-100b2ae1e0d8
rpi_yronyr_df = rpi_yronyr_df[['date', 'value']].apply(pd.Series)
rpi_yronyr_df['value'] = rpi_yronyr_df['value'].astype(float)
rpi_yronyr_df['value'] = 1 + rpi_yronyr_df['value'] / 100

rpi_yronyr_df['date'] = pd.to_datetime(rpi_yronyr_df['date'], format='%Y %b')
rpi_yronyr_df = rpi_yronyr_df.set_index(['date'])

rpi_yronyr_df.tail()
# %%
url = 'https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/l55o/mm23/data'

r = requests.get(url, headers=header)
# https://stackoverflow.com/questions/43590153/http-error-403-forbidden-when-reading-html
data = json.loads(r.text)
cpih_yronyr_df = pd.json_normalize(data, record_path=['months'])
#https://towardsdatascience.com/how-to-convert-json-into-a-pandas-dataframe-100b2ae1e0d8
cpih_yronyr_df = cpih_yronyr_df[['date', 'value']].apply(pd.Series)
cpih_yronyr_df['value'] = cpih_yronyr_df['value'].astype(float)
cpih_yronyr_df['value'] = 1 + cpih_yronyr_df['value'] / 100

#https://stackoverflow.com/questions/65612231/convert-string-month-year-to-datetime-in-pandas-dataframe

cpih_yronyr_df['date'] = pd.to_datetime(cpih_yronyr_df['date'], format='%Y %b')
cpih_yronyr_df = cpih_yronyr_df.set_index(['date'])

cpih_yronyr_df.tail()
# %%
from scipy import stats
rpi_yronyr_avg = stats.gmean(rpi_yronyr_df['value'])
cpih_yronyr_avg = stats.gmean(cpih_yronyr_df['value'])
print(rpi_yronyr_avg, cpih_yronyr_avg)
# %%
sp500 = yf.Ticker("IGUS.L")
hist = sp500.history(period="max", interval="1mo")
SP500_daily_returns = hist['Close'].to_frame()
SP500_daily_returns
# %%
# x_0 * r^t = x_t, r = (x_t/x_0)^(1/t)
gain = SP500_daily_returns['Close'][-1] / SP500_daily_returns['Close'][0]
days_elapsed = SP500_daily_returns.index[-1] - SP500_daily_returns.index[0]
SP500_daily_avg = gain ** (1/ days_elapsed.days) # average daily returns from hedged gbp https://www.ishares.com/uk/individual/en/products/251904/ishares-sp-500-gbp-hedged-ucits-etf#chartDialog
print(SP500_daily_avg)
#%%
days_elapsed = pd.Timestamp(2021, 5, 19) - pd.Timestamp(2010, 9, 30)
real_salary_growth = 0.02 # compared to cpi
real_avg_salary_growth = 0.01

# def monthly_income(i):
#     if i // 365 < 4: # in 4 year phd
#         return 30000 / 12
#     else:
#         return 120000 / 12 * (1 + cpi + real_salary_growth) ** (i // 365) # monthly income with salary increase yearly
def monthly_income(i):
        return 30000 / 12 * (cpih_yronyr_avg + real_salary_growth) ** (i // 365) # monthly income with salary increase yearly
def taxband_monthly_income(monthly_band, i):
    return monthly_band * (cpih_yronyr_avg + real_avg_salary_growth) ** (i // 365)
def monthly_repayment(days_elapsed):
    delta_income = monthly_income(days_elapsed) - taxband_monthly_income(27295/12, days_elapsed)
    if delta_income > 0:
        return delta_income * 0.09
    else:
        return 0
def working_interest(days_elapsed):
    income = monthly_income(days_elapsed)
    bottom_band = taxband_monthly_income(27295/12, days_elapsed)
    upper_band = taxband_monthly_income(49130/12, days_elapsed)
    delta_income = income - bottom_band
    if delta_income > 0:
        if income > upper_band:
            return (rpi_yronyr_avg + 0.03) ** (1 / 365) 
        else:
            return (rpi_yronyr_avg + delta_income / (upper_band - bottom_band) * 0.03) ** (1 / 365)  # linear interpolation with 0% at 27295 and 3% at 49130
    else:
        return 1
# %%
daterange = pd.date_range("2021-10-20", "2026-04-05")

debt = 0
interest = (rpi_yronyr_avg + 0.03) ** (1 / 365) 

for single_date in daterange:
    if pd.Timestamp("2021-10-20") == single_date or pd.Timestamp("2022-02-02") == single_date or pd.Timestamp("2022-10-19") == single_date or pd.Timestamp("2023-02-01") == single_date or pd.Timestamp("2023-10-18") == single_date or pd.Timestamp("2024-01-31") == single_date or pd.Timestamp("2024-10-17") == single_date or pd.Timestamp("2025-01-30") == single_date:
        debt += 4422/3 + .25 * 9250
    if pd.Timestamp("2022-05-04") == single_date or pd.Timestamp("2023-05-03") == single_date or pd.Timestamp("2024-05-02") == single_date or pd.Timestamp("2025-05-01") == single_date:
        debt += 4422/3 + .5 * 9250
    debt = debt * interest
# %%
payments = 0
npv_payments = 0
npv_SP500_payments = 0

daterange = pd.date_range("2026-04-06", "2056-04-05")
for single_date in daterange:
    days_elapsed = single_date - pd.Timestamp("2026-04-06")
    if single_date.day == 1:
        repayment = monthly_repayment(days_elapsed.days)
    else:
        repayment = 0
    interest = working_interest(days_elapsed.days)
    temp = debt * interest - repayment
    if temp < 0:
        repayment = debt * interest # if repayment > debt * interest
        debt = 0

        payments += repayment

        days_elapsed_from_freshers = single_date - pd.Timestamp("2021-10-20")
        npv_payments += repayment / ((rpi_yronyr_avg) ** (days_elapsed_from_freshers.days / 365))
        npv_SP500_payments += repayment / (SP500_daily_avg ** days_elapsed_from_freshers.days)
        
        print(single_date)
        break
    debt = temp

    payments += repayment

    days_elapsed_from_freshers = single_date - pd.Timestamp("2021-10-20")
    npv_payments += repayment / ((cpih_yronyr_avg) ** (days_elapsed_from_freshers.days / 365))
    npv_SP500_payments += repayment / (SP500_daily_avg ** days_elapsed_from_freshers.days)

print("Payments: %s, NPV: %s, NPV SP500: %s" %(payments, npv_payments, npv_SP500_payments))
# %%