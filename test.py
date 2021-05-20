#%%    
payments = 0
interest = (1 + rpi + 0.03) ** (1 / 12) 
for i in range(0, 30*12):
    repayment = (monthly_income(i) - base_monthly_income(i)) * 0.09
    temp = debt * interest - repayment
    if temp < 0:
        payments = payments + debt * interest
        debt = 0
        break
    debt = temp
    payments = payments + repayment
# %%
debt = 0 
for i in range(0, 4):
    debt += (9250 + 4422) * (1 + rpi + 0.03)
payments = 0
for i in range(0, 30):
    repayment = (50000 - 27295) * 0.09
    payments = payments + repayment