#!/usr/bin/env python3

import random
import fractions
from decimal import Decimal, getcontext
import operations

# Set decimal precision for percentage calculations
getcontext().prec = 6

# Operation type constants
OPERATION_ADD = 1
OPERATION_SUB = 2
OPERATION_MUL = 3
OPERATION_DIV = 4
OPERATION_FRAC = 5
OPERATION_PERC = 6
OPERATION_EXP = 7
OPERATION_ARRAY = 8
OPERATION_MIXED = 9


class QuestionGenerator:
    """
    Class to handle generation of math questions of various types and difficulty levels
    """
    
    @staticmethod
    def get_operation_name(operation_type):
        """Return the name of the operation type"""
        operations_map = {
            OPERATION_ADD: "Addition",
            OPERATION_SUB: "Subtraction",
            OPERATION_MUL: "Multiplication",
            OPERATION_DIV: "Division",
            OPERATION_FRAC: "Fractions",
            OPERATION_PERC: "Percentages",
            OPERATION_EXP: "Exponents",
            OPERATION_ARRAY: "Arrays",
            OPERATION_MIXED: "Mixed Challenge"
        }
        return operations_map.get(operation_type, "Unknown")
    
    @staticmethod
    def generate_question(operation_type, difficulty):
        """Generate a question based on operation type and difficulty"""
        if operation_type == OPERATION_ADD:
            return QuestionGenerator.generate_addition_question(difficulty)
        elif operation_type == OPERATION_SUB:
            return QuestionGenerator.generate_subtraction_question(difficulty)
        elif operation_type == OPERATION_MUL:
            return QuestionGenerator.generate_multiplication_question(difficulty)
        elif operation_type == OPERATION_DIV:
            return QuestionGenerator.generate_division_question(difficulty)
        elif operation_type == OPERATION_FRAC:
            return operations.generate_fraction_question(difficulty)
        elif operation_type == OPERATION_PERC:
            return operations.generate_percentage_question(difficulty)
        elif operation_type == OPERATION_EXP:
            return operations.generate_exponent_question(difficulty)
        elif operation_type == OPERATION_ARRAY:
            return operations.generate_array_question(difficulty)
        elif operation_type == OPERATION_MIXED:
            # For mixed challenge, pick a random operation type
            random_op = random.randint(1, 8)
            return QuestionGenerator.generate_question(random_op, difficulty)
        else:
            print("This operation is coming soon! Using addition for now.")
            return QuestionGenerator.generate_addition_question(difficulty)

    @staticmethod
    def generate_addition_question(difficulty):
        """Generate an addition question based on difficulty"""
        if difficulty == 1:  # Easy
            num1 = random.randint(1, 20)
            num2 = random.randint(1, 20)
        elif difficulty == 2:  # Medium
            num1 = random.randint(10, 100)
            num2 = random.randint(10, 100)
        else:  # Hard
            num1 = random.randint(50, 500)
            num2 = random.randint(50, 500)
        
        question = f"{num1} + {num2}"
        answer = num1 + num2
        return question, str(answer)

    @staticmethod
    def generate_subtraction_question(difficulty):
        """Generate a subtraction question based on difficulty"""
        if difficulty == 1:  # Easy
            num2 = random.randint(1, 10)
            num1 = random.randint(num2, 20)  # Ensure positive result
        elif difficulty == 2:  # Medium
            num2 = random.randint(10, 50)
            num1 = random.randint(num2, 100)
        else:  # Hard
            num2 = random.randint(50, 200)
            num1 = random.randint(num2, 500)
            
        question = f"{num1} - {num2}"
        answer = num1 - num2
        return question, str(answer)

    @staticmethod
    def generate_multiplication_question(difficulty):
        """Generate a multiplication question based on difficulty"""
        if difficulty == 1:  # Easy
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
        elif difficulty == 2:  # Medium
            num1 = random.randint(2, 12)
            num2 = random.randint(11, 30)
        else:  # Hard
            num1 = random.randint(11, 30)
            num2 = random.randint(11, 30)
            
        question = f"{num1} × {num2}"
        answer = num1 * num2
        return question, str(answer)

    @staticmethod
    def generate_division_question(difficulty):
        """Generate a division question based on difficulty"""
        if difficulty == 1:  # Easy - result is an integer
            divisor = random.randint(1, 10)
            result = random.randint(1, 10)
            dividend = divisor * result
        elif difficulty == 2:  # Medium - may have remainders
            divisor = random.randint(2, 15)
            dividend = random.randint(20, 150)
            # Adjust to avoid complex decimals
            if dividend % divisor != 0 and random.choice([True, False]):
                dividend = (dividend // divisor) * divisor
        else:  # Hard - larger numbers
            divisor = random.randint(5, 25)
            dividend = random.randint(100, 500)
            
        question = f"{dividend} ÷ {divisor}"
        
        # Calculate answer, format as float or integer as appropriate
        result = dividend / divisor
        if result == int(result):
            answer = str(int(result))
        else:
            # Round to 2 decimal places for cleaner answers
            answer = str(round(result, 2))
            
        return question, answer
        
    @staticmethod
    def normalize_answer(answer_str):
        """
        Normalize answer string to handle different formats
        """
        # Handle fractions
        if '/' in answer_str:
            try:
                num, denom = map(int, answer_str.split('/'))
                return fractions.Fraction(num, denom)
            except (ValueError, ZeroDivisionError):
                return answer_str
                
        # Handle decimal numbers
        try:
            value = float(answer_str)
            # If it's a whole number, convert to int
            if value == int(value):
                return int(value)
            return value
        except ValueError:
            return answer_str
