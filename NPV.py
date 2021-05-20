#%%
import pandas as pd
rpi = 0.026
cpi = 0.01
days_elapsed = pd.Timestamp(2021, 5, 19) - pd.Timestamp(2010, 9, 30)
SP500_daily = 3.0273 ** (1/ days_elapsed.days) # average daily returns from hedged gbp https://www.ishares.com/uk/individual/en/products/251904/ishares-sp-500-gbp-hedged-ucits-etf#chartDialog
real_salary_growth = 0.03 # compared to cpi
real_avg_salary_growth = 0.01

# def monthly_income(i):
    # if i // 365 < 4: # in 4 year phd
        # return 30000 / 12
    # else:
        # return 120000 / 12 * (1 + cpi + real_salary_growth) ** (i // 365) # monthly income with salary increase yearly
def monthly_income(i):
        return 40000 / 12 * (1 + cpi + real_salary_growth) ** (i // 365) # monthly income with salary increase yearly
def taxband_monthly_income(monthly_band, i):
    return monthly_band * (1 + cpi + real_avg_salary_growth) ** (i // 365)
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
            return (1 + rpi + 0.03) ** (1 / 365) 
        else:
            return (1 + rpi + delta_income / (upper_band - bottom_band) * 0.03) ** (1 / 365)  # linear interpolation with 0% at 27295 and 3% at 49130
    else:
        return 0
# %%
daterange = pd.date_range("2021-10-05", "2026-04-05")

debt = 0
interest = (1 + rpi + 0.03) ** (1 / 365) 

for single_date in daterange:
    if pd.Timestamp("2021-10-05") == single_date or pd.Timestamp("2022-01-18") == single_date or pd.Timestamp("2022-10-04") == single_date or pd.Timestamp("2023-01-17") == single_date or pd.Timestamp("2023-10-03") == single_date or pd.Timestamp("2024-01-16") == single_date or pd.Timestamp("2024-10-02") == single_date or pd.Timestamp("2025-01-15") == single_date:
        debt += 4422/3 + .25 * 9250
    if pd.Timestamp("2022-04-26") == single_date or pd.Timestamp("2023-04-25") == single_date or pd.Timestamp("2024-04-24") == single_date or pd.Timestamp("2025-04-23") == single_date:
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
        payments = payments + debt * interest # if repayment > debt * interest
        debt = 0
        print(single_date)
        break
    debt = temp
    
    payments += repayment

    days_elapsed_from_freshers = single_date - pd.Timestamp("2021-10-05")
    npv_payments += repayment / ((1 + cpi) ** (days_elapsed_from_freshers.days / 365))
    npv_SP500_payments += repayment / (SP500_daily ** days_elapsed_from_freshers.days)
# %%
