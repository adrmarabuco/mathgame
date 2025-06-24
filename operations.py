#!/usr/bin/env python3

import random
import fractions
from decimal import Decimal, getcontext

# Set decimal precision for percentage calculations
getcontext().prec = 6

def generate_fraction_question(difficulty):
    """Generate a fraction operation question based on difficulty"""
    operation = random.choice(['+', '-', '×', '÷'])
    
    if difficulty == 1:  # Easy
        # Use fractions with small denominators
        denom1 = random.choice([2, 3, 4, 5])
        denom2 = random.choice([2, 3, 4, 5])
        num1 = random.randint(1, denom1-1)
        num2 = random.randint(1, denom2-1)
    elif difficulty == 2:  # Medium
        denom1 = random.choice([4, 5, 6, 8, 10])
        denom2 = random.choice([4, 5, 6, 8, 10])
        num1 = random.randint(1, denom1)
        num2 = random.randint(1, denom2)
    else:  # Hard
        denom1 = random.choice([6, 8, 9, 12, 15, 16])
        denom2 = random.choice([6, 8, 9, 12, 15, 16])
        num1 = random.randint(1, denom1*2)
        num2 = random.randint(1, denom2)
    
    # Create fraction objects
    frac1 = fractions.Fraction(num1, denom1)
    frac2 = fractions.Fraction(num2, denom2)
    
    # Format question string with proper fraction notation
    question = f"{num1}/{denom1} {operation} {num2}/{denom2}"
    
    # Calculate answer based on operation
    if operation == '+':
        answer = frac1 + frac2
    elif operation == '-':
        # Swap if needed to ensure positive result for easier problems
        if difficulty < 3 and frac2 > frac1:
            frac1, frac2 = frac2, frac1
            question = f"{frac1.numerator}/{frac1.denominator} - {frac2.numerator}/{frac2.denominator}"
        answer = frac1 - frac2
    elif operation == '×':
        answer = frac1 * frac2
    elif operation == '÷':
        # Avoid division by zero
        if frac2.numerator == 0:
            frac2 = fractions.Fraction(1, denom2)
            question = f"{num1}/{denom1} {operation} 1/{denom2}"
        answer = frac1 / frac2
    
    # Convert answer to string representation
    if answer.denominator == 1:
        answer_str = str(answer.numerator)
    else:
        answer_str = f"{answer.numerator}/{answer.denominator}"
    
    return question, answer_str


def generate_percentage_question(difficulty):
    """Generate a percentage-based question"""
    q_type = random.randint(1, 3)
    
    if difficulty == 1:  # Easy
        # Find X% of Y
        if q_type == 1:
            percentage = random.choice([10, 25, 50, 75, 100])
            number = random.randint(1, 100) * 4  # Multiple of 4 for easier calculations
            answer = (percentage / 100) * number
            question = f"What is {percentage}% of {number}?"
        # X is what % of Y
        elif q_type == 2:
            y = random.randint(5, 10) * 10  # 50, 60, ..., 100
            percentage = random.choice([10, 20, 25, 50, 75])
            x = int((percentage / 100) * y)
            question = f"{x} is what percent of {y}?"
            answer = percentage
        # X + Y%
        else:
            number = random.randint(10, 100) * 10  # 100, 200, ..., 1000
            percentage = random.choice([5, 10, 25, 50, 100])
            answer = number * (1 + percentage/100)
            question = f"{number} + {percentage}%"
    
    elif difficulty == 2:  # Medium
        # Find X% of Y
        if q_type == 1:
            percentage = random.randint(1, 99)
            number = random.randint(1, 200)
            answer = (percentage / 100) * number
            question = f"What is {percentage}% of {number}?"
        # X is what % of Y
        elif q_type == 2:
            y = random.randint(50, 200)
            x = random.randint(5, y)
            percentage = round((x / y) * 100, 1)
            question = f"{x} is what percent of {y}?"
            answer = percentage
        # X + Y%
        else:
            number = random.randint(100, 500)
            percentage = random.randint(1, 40)
            answer = number * (1 + percentage/100)
            question = f"{number} + {percentage}%"
            
    else:  # Hard
        # Find X% of Y with complex numbers
        if q_type == 1:
            percentage = random.randint(1, 999) / 10  # Allow decimals
            number = random.randint(100, 500)
            answer = (percentage / 100) * number
            question = f"What is {percentage}% of {number}?"
        # X is what % of Y with challenging numbers
        elif q_type == 2:
            y = random.randint(50, 500)
            x = random.randint(1, y)
            percentage = round((x / y) * 100, 2)
            question = f"{x} is what percent of {y}?"
            answer = percentage
        # X - Y%
        else:
            number = random.randint(500, 1000)
            percentage = random.randint(1, 75)
            answer = number * (1 - percentage/100)
            question = f"{number} - {percentage}%"
    
    # Round the answer to 2 decimal places if it's a float
    if isinstance(answer, float):
        answer = round(answer, 2)
    
    return question, str(answer)


def generate_exponent_question(difficulty):
    """Generate exponentiation and root questions"""
    # Choose operation type based on difficulty
    if difficulty == 1:  # Easy
        op_type = random.choice(['square', 'cube', 'square_root_perfect'])
    elif difficulty == 2:  # Medium
        op_type = random.choice(['square', 'cube', 'power', 'square_root'])
    else:  # Hard
        op_type = random.choice(['power', 'power_fraction', 'root', 'combined'])
    
    # Generate question based on operation type
    if op_type == 'square':
        base = random.randint(2, 15 if difficulty == 1 else 25)
        question = f"{base}²"
        answer = base ** 2
        
    elif op_type == 'cube':
        base = random.randint(2, 10 if difficulty == 1 else 15)
        question = f"{base}³"
        answer = base ** 3
        
    elif op_type == 'power':
        base = random.randint(2, 6 if difficulty == 2 else 10)
        exponent = random.randint(2, 4 if difficulty == 2 else 6)
        question = f"{base}^{exponent}"
        answer = base ** exponent
        
    elif op_type == 'power_fraction':
        base = random.randint(2, 10) ** 2  # Perfect square
        exponent = fractions.Fraction(1, 2)
        question = f"{base}^(1/2)"
        answer = int(base ** 0.5)
        
    elif op_type == 'square_root_perfect':
        result = random.randint(2, 10)
        number = result * result
        question = f"√{number}"
        answer = result
        
    elif op_type == 'square_root':
        number = random.randint(2, 100)
        question = f"√{number}"
        answer = round(number ** 0.5, 3)
        
    elif op_type == 'root':
        root = random.randint(2, 3)
        result = random.randint(2, 5)
        number = result ** root
        if root == 2:
            question = f"√{number}"
        elif root == 3:
            question = f"∛{number}"
        else:
            question = f"{number}^(1/{root})"
        answer = result
        
    elif op_type == 'combined':
        base = random.randint(2, 5)
        exp1 = random.randint(2, 3)
        exp2 = random.randint(2, 3)
        question = f"{base}^{exp1} × {base}^{exp2}"
        answer = base ** (exp1 + exp2)
    
    # Ensure the answer is properly formatted
    if isinstance(answer, float) and answer.is_integer():
        answer = int(answer)
    if isinstance(answer, float):
        answer = round(answer, 3)
    
    return question, str(answer)


def generate_array_question(difficulty):
    """Generate questions about array operations"""
    # Define array size based on difficulty
    if difficulty == 1:  # Easy
        size = random.randint(3, 5)
        elements = [random.randint(1, 10) for _ in range(size)]
    elif difficulty == 2:  # Medium
        size = random.randint(5, 8)
        elements = [random.randint(1, 20) for _ in range(size)]
    else:  # Hard
        size = random.randint(6, 10)
        elements = [random.randint(-10, 30) for _ in range(size)]
    
    # Choose operation type
    if difficulty == 1:
        op_type = random.choice(['sum', 'max', 'min', 'mean'])
    elif difficulty == 2:
        op_type = random.choice(['sum', 'max', 'min', 'mean', 'median', 'product_first_n'])
    else:
        op_type = random.choice(['sum', 'max', 'min', 'mean', 'median', 'product_first_n', 'sum_even', 'sum_odd'])
    
    # Format array for display
    array_str = "[" + ", ".join(str(x) for x in elements) + "]"
    
    # Generate question and answer based on operation type
    if op_type == 'sum':
        question = f"Sum of {array_str}"
        answer = sum(elements)
        
    elif op_type == 'max':
        question = f"Max value in {array_str}"
        answer = max(elements)
        
    elif op_type == 'min':
        question = f"Min value in {array_str}"
        answer = min(elements)
        
    elif op_type == 'mean':
        question = f"Mean (average) of {array_str}"
        answer = round(sum(elements) / len(elements), 2)
        
    elif op_type == 'median':
        question = f"Median of {array_str}"
        sorted_elements = sorted(elements)
        mid = len(sorted_elements) // 2
        if len(sorted_elements) % 2 == 0:
            answer = (sorted_elements[mid-1] + sorted_elements[mid]) / 2
        else:
            answer = sorted_elements[mid]
        if isinstance(answer, float) and answer.is_integer():
            answer = int(answer)
        
    elif op_type == 'product_first_n':
        n = random.randint(2, min(4, len(elements)))
        question = f"Product of first {n} elements in {array_str}"
        answer = 1
        for i in range(n):
            answer *= elements[i]
        
    elif op_type == 'sum_even':
        question = f"Sum of even values in {array_str}"
        answer = sum(x for x in elements if x % 2 == 0)
        
    elif op_type == 'sum_odd':
        question = f"Sum of odd values in {array_str}"
        answer = sum(x for x in elements if x % 2 != 0)
    
    # Ensure the answer is properly formatted
    if isinstance(answer, float) and answer.is_integer():
        answer = int(answer)
    
    return question, str(answer)
