import json
import warnings
import pandas as pd
import numpy as np
import boto3
import uvicorn
from fastapi import FastAPI, HTTPException
# from mangum import Mangum
from pydantic import BaseModel
warnings.filterwarnings('ignore')

# Create FastAPI application
app = FastAPI()

class SendIn(BaseModel):
    salary: float
    monthly_interest: float
    loan_tenor: int

def calculate_loan_amount(salary: float, monthly_interest: float, loan_tenor: int) -> tuple:
    """
    Calculate loan-related values based on provided inputs.

    This function calculates various loan-related values based on the given salary, monthly interest rate,
    and loan tenor. It considers the monthly repayment limit as 50% of the salary.

    Args:
        salary (float): The net salary of the customer.
        monthly_interest (float): The interest rate on the loan per month (in percentage).
        loan_tenor (int): The preferred loan tenor in months (3, 6, or 12 months).

    Returns:
        tuple: A tuple containing the following loan-related values:
            - recommended_loan_amount (float): The total loan amount that can be disbursed.
            - principal (float): The principal loan amount (excluding interest).
            - total_interest (float): The total interest paid over the loan tenor.
            - monthly_repayment (float): The monthly repayment amount, including both principal and interest.
    """
    monthly_repayment_limit = 0.3 * salary
    cumulative_interest = (monthly_interest * loan_tenor) / 100
    loan_amount = (monthly_repayment_limit * ((1 - (1 + cumulative_interest)**(-loan_tenor)) / cumulative_interest))
    principal = loan_amount - ((monthly_interest / 100) * loan_amount)
    total_interest = (monthly_interest * loan_tenor)
    monthly_repayment = loan_amount / loan_tenor

    return (
        round(loan_amount, 2),
        round(principal, 2),
        round(total_interest, 2),
        round(monthly_repayment, 2)
    )

@app.post("/recommend_loan")
async def recommend_loan_amount(data: SendIn):
    if data.loan_tenor not in [3, 6, 12]:
        raise HTTPException(status_code=400, detail="Loan tenor must be 3, 6, or 12 months")
    
    loan_amount, principal, interest_rate, monthly_repayment = calculate_loan_amount(data.salary, data.monthly_interest, data.loan_tenor)
    return {"recommended_loan_amount": loan_amount,
            "principal amount": principal,
            "cummulative interest": interest_rate,
            "monthly installment": monthly_repayment}
