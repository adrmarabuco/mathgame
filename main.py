#!/usr/bin/env python3

import random
from datetime import datetime
import os
import time
import fractions
from decimal import Decimal, getcontext

# Import our advanced operations
import operations

# Pythonista-specific import - will be used if available
try:
    import console
    IS_PYTHONISTA = True
except ImportError:
    IS_PYTHONISTA = False

# Constants
APP_NAME = "MathMaster"
MAX_ROUNDS = 10

# Scoring constants
POINTS_BASE = 100  # Base points for correct answer
POINTS_SPEED_BONUS_THRESHOLD = 5.0  # Seconds threshold for speed bonus
POINTS_SPEED_BONUS = 50  # Bonus for quick answers
POINTS_DIFFICULTY_MULTIPLIER = [1, 1.5, 2.5]  # Multipliers for each difficulty level
STREAK_BONUS_THRESHOLD = 3  # Number of correct answers in a row to get streak bonus
STREAK_BONUS = 25  # Points for maintaining a streak

# Operation Types
OPERATION_ADD = "addition"
OPERATION_SUB = "subtraction"
OPERATION_MUL = "multiplication"
OPERATION_DIV = "division"
OPERATION_FRAC = "fractions"
OPERATION_PERC = "percentages"
OPERATION_EXP = "exponents"
OPERATION_ARRAY = "arrays"


def clear_screen():
    """Clear the terminal screen in a cross-platform way"""
    if IS_PYTHONISTA:
        console.clear()
    else:
        os.system('cls' if os.name == 'nt' else 'clear')


def display_welcome():
    """Display welcome message"""
    clear_screen()
    print(f"\n{'-'*50}")
    print(f"{APP_NAME}".center(50))
    print(f"A math skills training game".center(50))
    print(f"{'-'*50}\n")


def get_operation_choice():
    """Get user's choice of operation"""
    print("\nChoose an operation type:")
    print("1. Addition")
    print("2. Subtraction")
    print("3. Multiplication")
    print("4. Division")
    print("5. Fractions")
    print("6. Percentages")
    print("7. Exponents")
    print("8. Arrays")
    print("9. Mixed Challenge")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-9): "))
            if 1 <= choice <= 9:
                return choice
            print("Please enter a number between 1 and 9.")
        except ValueError:
            print("Please enter a valid number.")


def get_difficulty():
    """Get user's preferred difficulty level"""
    print("\nChoose difficulty level:")
    print("1. Easy - Simple operations with smaller numbers")
    print("2. Medium - More complex operations with larger numbers")
    print("3. Hard - Complex operations with challenging numbers")
    print("4. Adaptive - Adjusts difficulty based on your performance")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-4): "))
            if 1 <= choice <= 4:
                return choice
            print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Please enter a valid number.")


def generate_addition_question(difficulty):
    """Generate an addition question based on difficulty"""
    if difficulty == 1:  # Easy
        x = random.randint(1, 20)
        y = random.randint(1, 20)
    elif difficulty == 2:  # Medium
        x = random.randint(10, 99)
        y = random.randint(10, 99)
    else:  # Hard
        x = random.randint(100, 999)
        y = random.randint(100, 999)
    
    question = f"{x} + {y}"
    answer = x + y
    return question, answer


def generate_subtraction_question(difficulty):
    """Generate a subtraction question based on difficulty"""
    if difficulty == 1:  # Easy
        y = random.randint(1, 10)
        x = random.randint(y, 20)  # Ensure x >= y for positive result
    elif difficulty == 2:  # Medium
        y = random.randint(10, 50)
        x = random.randint(y, 99)
    else:  # Hard
        y = random.randint(100, 500)
        x = random.randint(y, 999)
    
    question = f"{x} - {y}"
    answer = x - y
    return question, answer


def generate_multiplication_question(difficulty):
    """Generate a multiplication question based on difficulty"""
    if difficulty == 1:  # Easy
        x = random.randint(1, 10)
        y = random.randint(1, 10)
    elif difficulty == 2:  # Medium
        x = random.randint(5, 20)
        y = random.randint(5, 20)
    else:  # Hard
        x = random.randint(10, 99)
        y = random.randint(10, 30)
    
    question = f"{x} × {y}"
    answer = x * y
    return question, answer


def generate_division_question(difficulty):
    """Generate a division question with whole number result"""
    if difficulty == 1:  # Easy
        y = random.randint(1, 10)
        multiple = random.randint(1, 10)
        x = y * multiple
    elif difficulty == 2:  # Medium
        y = random.randint(2, 12)
        multiple = random.randint(1, 20)
        x = y * multiple
    else:  # Hard
        y = random.randint(2, 25)
        multiple = random.randint(10, 40)
        x = y * multiple
    
    question = f"{x} ÷ {y}"
    answer = x // y
    return question, answer


def generate_question(operation_type, difficulty):
    """Generate a question based on operation type and difficulty"""
    if operation_type == 1:  # Addition
        return generate_addition_question(difficulty)
    elif operation_type == 2:  # Subtraction
        return generate_subtraction_question(difficulty)
    elif operation_type == 3:  # Multiplication
        return generate_multiplication_question(difficulty)
    elif operation_type == 4:  # Division
        return generate_division_question(difficulty)
    elif operation_type == 5:  # Fractions
        return operations.generate_fraction_question(difficulty)
    elif operation_type == 6:  # Percentages
        return operations.generate_percentage_question(difficulty)
    elif operation_type == 7:  # Exponents
        return operations.generate_exponent_question(difficulty)
    elif operation_type == 8:  # Arrays
        return operations.generate_array_question(difficulty)
    elif operation_type == 9:  # Mixed challenge
        # Choose a random operation, including advanced ones
        random_op = random.randint(1, 8)  # All operation types
        return generate_question(random_op, difficulty)
    else:
        # Default to addition if operation not implemented
        print("This operation is coming soon! Using addition for now.")
        return generate_addition_question(difficulty)


def calculate_score(is_correct, time_taken, difficulty, streak_count):
    """Calculate score based on correctness, time, and difficulty"""
    if not is_correct:
        return 0
    
    # Base score for correct answer
    score = POINTS_BASE * POINTS_DIFFICULTY_MULTIPLIER[difficulty - 1]
    
    # Speed bonus for quick answers
    if time_taken < POINTS_SPEED_BONUS_THRESHOLD:
        speed_factor = max(0, (POINTS_SPEED_BONUS_THRESHOLD - time_taken) / POINTS_SPEED_BONUS_THRESHOLD)
        score += POINTS_SPEED_BONUS * speed_factor
    
    # Streak bonus
    if streak_count >= STREAK_BONUS_THRESHOLD:
        score += STREAK_BONUS * (1 + (streak_count - STREAK_BONUS_THRESHOLD) * 0.1)
    
    return int(score)


def play_round(operation_type, difficulty, round_num, total_rounds, streak_count=0):
    """Play a single round of the game"""
    clear_screen()
    print(f"\nRound {round_num} of {total_rounds}")
    print(f"{'='*30}\n")
    
    question, correct_answer = generate_question(operation_type, difficulty)
    
    print(f"Calculate: {question}")
    start_time = datetime.now()
    
    # Get user's answer
    try:
        # Handle different answer formats based on operation type
        if operation_type == 5:  # Fractions
            user_input = input("Your answer (as a/b or decimal): ")
            if '/' in user_input:
                parts = user_input.split('/')
                if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
                    num = int(parts[0].strip())
                    denom = int(parts[1].strip())
                    if denom != 0:  # Avoid division by zero
                        user_answer = f"{num}/{denom}"
                    else:
                        user_answer = None
                else:
                    user_answer = None
            else:
                try:
                    # Try to convert input to fraction in lowest terms
                    decimal = float(user_input)
                    frac = fractions.Fraction(decimal).limit_denominator(1000)
                    user_answer = f"{frac.numerator}/{frac.denominator}" if frac.denominator != 1 else str(frac.numerator)
                except ValueError:
                    user_answer = None
        elif operation_type == 6:  # Percentages
            user_input = input("Your answer: ")
            try:
                if '%' in user_input:
                    user_input = user_input.replace('%', '')
                user_answer = str(float(user_input))
                # Remove trailing zeros for cleaner display
                if '.' in user_answer:
                    user_answer = user_answer.rstrip('0').rstrip('.')
            except ValueError:
                user_answer = None
        elif operation_type in (7, 8):  # Exponents and Arrays might have float answers
            user_input = input("Your answer: ")
            try:
                user_answer = str(float(user_input))
                # Remove trailing zeros for cleaner display
                if '.' in user_answer:
                    user_answer = user_answer.rstrip('0').rstrip('.')
            except ValueError:
                user_answer = None
        else:  # Basic operations
            user_answer = input("Your answer: ")
            try:
                user_answer = str(int(user_answer))
            except ValueError:
                try:
                    user_answer = str(float(user_answer))
                    if '.' in user_answer:
                        user_answer = user_answer.rstrip('0').rstrip('.')
                except ValueError:
                    user_answer = None
    except ValueError:
        user_answer = None
    
    end_time = datetime.now()
    time_taken = end_time - start_time
    
    # Check answer - compare as strings to handle fractions, decimals, etc.
    # For fractions, normalize both sides to handle equivalent fractions
    is_correct = False
    
    if user_answer is not None:
        # Try to normalize fractions for comparison
        try:
            # Convert both to fractions if possible
            if '/' in str(user_answer) and '/' in str(correct_answer):
                user_parts = str(user_answer).split('/')
                correct_parts = str(correct_answer).split('/')
                
                if len(user_parts) == 2 and len(correct_parts) == 2:
                    user_frac = fractions.Fraction(int(user_parts[0]), int(user_parts[1]))
                    correct_frac = fractions.Fraction(int(correct_parts[0]), int(correct_parts[1]))
                    is_correct = (user_frac == correct_frac)
            # Handle float comparisons with small tolerance
            elif '.' in str(user_answer) or '.' in str(correct_answer):
                try:
                    user_float = float(user_answer)
                    correct_float = float(correct_answer)
                    # Allow small tolerance for floating point
                    is_correct = abs(user_float - correct_float) < 0.001
                except ValueError:
                    is_correct = False
            else:
                # Direct string comparison for integers and other formats
                is_correct = (str(user_answer) == str(correct_answer))
        except (ValueError, ZeroDivisionError):
            # If any conversion fails, fall back to direct comparison
            is_correct = (str(user_answer) == str(correct_answer))
    
    # Show result
    if is_correct:
        print(f"\n✓ Correct! The answer is {correct_answer}")
        print(f"Time: {time_taken.total_seconds():.2f} seconds")
    else:
        print(f"\n✗ Incorrect. The correct answer is {correct_answer}")
        print(f"Time: {time_taken.total_seconds():.2f} seconds")
    
    # Calculate score
    score = calculate_score(is_correct, time_taken.total_seconds(), difficulty, streak_count)
    
    # Display score if correct
    if is_correct:
        print(f"Score: +{score} points")
    
    # Pause between rounds
    input("\nPress Enter to continue...")
    
    return {
        'correct': is_correct,
        'time_taken': time_taken.total_seconds(),
        'question': question,
        'user_answer': user_answer,
        'correct_answer': correct_answer,
        'score': score
    }


def display_game_summary(results):
    """Display a summary of game results"""
    clear_screen()
    print("\n" + "="*50)
    print("GAME SUMMARY".center(50))
    print("="*50)
    
    # Calculate stats
    total_rounds = len(results)
    correct_count = sum(1 for r in results if r['correct'])
    accuracy = (correct_count / total_rounds) * 100 if total_rounds > 0 else 0
    avg_time = sum(r['time_taken'] for r in results) / total_rounds if total_rounds > 0 else 0
    total_score = sum(r.get('score', 0) for r in results)
    
    # Display stats
    print(f"\nTotal Questions: {total_rounds}")
    print(f"Correct Answers: {correct_count}")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"Average Time: {avg_time:.2f} seconds")
    print(f"Total Score: {total_score} points")
    
    # Display individual results
    print("\n" + "-"*50)
    print("QUESTION REVIEW".center(50))
    print("-"*50)
    
    for i, result in enumerate(results, 1):
        status = "✓" if result['correct'] else "✗"
        print(f"{i}. {status} {result['question']} = {result['correct_answer']}")
        print(f"   Your answer: {result['user_answer']} ({result['time_taken']:.2f}s)")
    
    print("\n" + "="*50)
    input("\nPress Enter to return to the main menu...")


def main():
    """Main game loop"""
    while True:
        display_welcome()
        
        # Get game parameters
        operation_type = get_operation_choice()
        difficulty_choice = get_difficulty()
        
        # Set initial difficulty level (1-3)
        if difficulty_choice < 4:
            difficulty = difficulty_choice
            adaptive_difficulty = False
        else:
            difficulty = 1  # Start with easy
            adaptive_difficulty = True
        
        # Ask for number of rounds
        clear_screen()
        print("\nHow many rounds would you like to play?")
        print(f"(Default: {MAX_ROUNDS}, max: 50)")
        
        try:
            rounds = int(input("Number of rounds: ") or MAX_ROUNDS)
            rounds = min(max(1, rounds), 50)  # Between 1 and 50
        except ValueError:
            rounds = MAX_ROUNDS
        
        # Initialize results storage and streak counter
        results = []
        streak_count = 0
        
        # Play rounds
        for round_num in range(1, rounds + 1):
            round_result = play_round(operation_type, difficulty, round_num, rounds, streak_count)
            results.append(round_result)
            
            # Update streak count
            if round_result['correct']:
                streak_count += 1
                if streak_count >= STREAK_BONUS_THRESHOLD and streak_count % STREAK_BONUS_THRESHOLD == 0:
                    print(f"\n🔥 {streak_count} ANSWER STREAK! 🔥")
            else:
                # Reset streak on wrong answer
                if streak_count >= STREAK_BONUS_THRESHOLD:
                    print("\nStreak broken!")
                streak_count = 0
                
            # Adjust difficulty if adaptive mode is on
            if adaptive_difficulty and round_num % 3 == 0:  # Check every 3 rounds
                # Get the last 3 rounds or fewer if not enough
                recent_results = results[-3:]
                correct_count = sum(1 for r in recent_results if r['correct'])
                avg_time = sum(r['time_taken'] for r in recent_results) / len(recent_results)
                
                # Adjust difficulty based on performance
                if correct_count == 3 and avg_time < 5.0:  # All correct and fast
                    difficulty = min(3, difficulty + 1)  # Increase difficulty (max 3)
                    if difficulty > 1:  # Only show message if it increased
                        print(f"\n⬆️ Difficulty increased to {['Easy', 'Medium', 'Hard'][difficulty-1]} based on your performance! ⬆️")
                elif correct_count <= 1:  # Poor performance
                    difficulty = max(1, difficulty - 1)  # Decrease difficulty (min 1)
                    if difficulty < 3:  # Only show message if it decreased
                        print(f"\n⬇️ Difficulty adjusted to {['Easy', 'Medium', 'Hard'][difficulty-1]} to help you improve. ⬇️")
        
        # Show game summary
        display_game_summary(results)
        
        # Ask to play again
        print("\nWould you like to play again?")
        play_again = input("(y/n): ").lower()
        if play_again != 'y':
            clear_screen()
            print("\nThank you for playing MathMaster!\n")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print("\nGame interrupted. Thanks for playing!\n")