#!/usr/bin/env python3

import os
import time
from datetime import datetime
from questions import QuestionGenerator, OPERATION_MIXED

# Pythonista-specific import - used if available for better mobile experience
try:
    import console
    IS_PYTHONISTA = True
except ImportError:
    IS_PYTHONISTA = False


class MathGameCLI:
    """
    Command-line interface handler for MathMaster game
    """
    def __init__(self):
        self.operation_names = {
            1: "Addition",
            2: "Subtraction",
            3: "Multiplication",
            4: "Division",
            5: "Fractions",
            6: "Percentages",
            7: "Exponents",
            8: "Arrays",
            9: "Mixed Challenge"
        }
        
    def clear_screen(self):
        """Clear screen using appropriate method based on platform"""
        if IS_PYTHONISTA:
            console.clear()
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            
    def display_title(self):
        """Display game title"""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("                    M A T H  M A S T E R                   ")
        print("=" * 60)
        print("Improve your mental math skills with practice and challenges!")
        print("=" * 60 + "\n")
        
    def get_menu_choice(self, prompt, options, allow_quit=True):
        """
        Get a validated menu choice from user
        
        Args:
            prompt: The question to ask the user
            options: Dictionary of {option_number: option_name}
            allow_quit: Whether to allow 'q' to quit
            
        Returns:
            Selected option number or None if quit
        """
        while True:
            print(f"\n{prompt}")
            for key, value in sorted(options.items()):
                print(f"{key}. {value}")
                
            if allow_quit:
                print("q. Quit")
                
            choice = input("\nEnter your choice: ").strip().lower()
            
            if allow_quit and choice == 'q':
                return None
                
            try:
                choice = int(choice)
                if choice in options:
                    return choice
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
                
    def get_numeric_input(self, prompt, min_val=None, max_val=None, allow_float=False, default=None):
        """
        Get a validated numeric input from user
        
        Args:
            prompt: The question to ask the user
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            allow_float: Whether to allow floating point numbers
            default: Default value if empty input
            
        Returns:
            Validated numeric value
        """
        while True:
            try:
                user_input = input(prompt).strip()
                if not user_input and default is not None:
                    return default
                    
                value = float(user_input) if allow_float else int(user_input)
                
                if (min_val is not None and value < min_val) or (max_val is not None and value > max_val):
                    print(f"Value must be between {min_val} and {max_val}.")
                    continue
                    
                return value
            except ValueError:
                print("Please enter a valid number.")
                
    def show_operation_menu(self):
        """Show the operation selection menu and get choice"""
        return self.get_menu_choice(
            "Choose an operation to practice:",
            self.operation_names
        )
        
    def show_difficulty_menu(self):
        """Show the difficulty selection menu and get choice"""
        difficulty_options = {
            1: "Easy",
            2: "Medium",
            3: "Hard",
            4: "Adaptive (adjusts based on your performance)"
        }
        return self.get_menu_choice(
            "Select difficulty level:",
            difficulty_options
        )
        
    def show_game_mode_menu(self):
        """Show the game mode selection menu and get choice"""
        mode_options = {
            1: "Normal Mode (fixed number of rounds)",
            2: "Timed Challenge (solve as many as possible in 60 seconds)"
        }
        return self.get_menu_choice(
            "Select game mode:",
            mode_options
        )
        
    def get_rounds(self):
        """Get number of rounds from user"""
        return self.get_numeric_input(
            "How many rounds would you like to play? (1-20, default 10): ", 
            min_val=1, 
            max_val=20, 
            default=10
        )
        
    def get_time_limit(self):
        """Get time limit for timed mode from user"""
        return self.get_numeric_input(
            "Set time limit in seconds (30-300, default 60): ",
            min_val=30,
            max_val=300,
            default=60
        )
        
    def get_answer(self, question):
        """Get answer from user with validation"""
        print(f"Calculate: {question}")
        
        # Determine if this might need a fraction or decimal answer
        allow_float = '/' in question or '.' in question or '÷' in question
        
        while True:
            try:
                user_answer = input("Your answer: ").strip()
                
                # Handle empty input
                if not user_answer:
                    print("Please enter an answer.")
                    continue
                    
                # Handle fraction input (format: a/b)
                if '/' in user_answer:
                    parts = user_answer.split('/')
                    if len(parts) != 2:
                        print("Invalid fraction format. Use a/b format.")
                        continue
                    try:
                        numerator = int(parts[0])
                        denominator = int(parts[1])
                        if denominator == 0:
                            print("Denominator cannot be zero.")
                            continue
                        return user_answer
                    except ValueError:
                        print("Invalid fraction. Use integers for numerator and denominator.")
                        continue
                
                # Handle decimal or integer
                try:
                    if allow_float:
                        float(user_answer)  # Just to validate
                    else:
                        int(user_answer)  # Just to validate
                    return user_answer
                except ValueError:
                    print("Please enter a valid number.")
            except (KeyboardInterrupt, EOFError):
                return None
                
    def get_answer_timed(self, question, round_num, remaining_time):
        """Get answer with time tracking for timed mode"""
        self.clear_screen()
        print(f"\nTime remaining: {int(remaining_time)} seconds")
        print(f"Question {round_num}")
        print(f"Calculate: {question}")
        
        start_time = datetime.now()
        
        try:
            user_answer = input("Your answer: ").strip()
            time_taken = (datetime.now() - start_time).total_seconds()
            
            if not user_answer:
                return None, time_taken
                
            return user_answer, time_taken
        except (KeyboardInterrupt, EOFError):
            return "__QUIT__", 0
            
    def show_round_result(self, result, score, streak_message=None):
        """Show the result of a round"""
        correct_str = "CORRECT!" if result['correct'] else "INCORRECT!"
        answer_str = f"The correct answer is {result['correct_answer']}"
        time_str = f"Time: {result['time_taken']:.2f} seconds"
        score_str = f"Score: +{score}" if result['correct'] else "Score: +0"
        
        print(f"\n{correct_str}")
        if not result['correct']:
            print(answer_str)
        print(time_str)
        print(score_str)
        
        if streak_message:
            print(f"\n{streak_message}")
            
        print("\nPress Enter to continue...")
        input()
        
    def show_difficulty_change(self, message):
        """Show difficulty change message"""
        print(f"\n{message}")
        time.sleep(1.5)
        
    def show_game_summary(self, stats):
        """Show game summary statistics"""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("                   GAME SUMMARY                   ")
        print("=" * 60)
        
        print(f"Rounds played: {stats['total_rounds']}")
        print(f"Correct answers: {stats['correct_count']}/{stats['total_rounds']}")
        print(f"Accuracy: {stats['accuracy']:.1f}%")
        print(f"Average time per question: {stats['avg_time']:.2f} seconds")
        print(f"Total score: {stats['total_score']}")
        print("=" * 60)
        
        print("\nPress Enter to return to the main menu...")
        input()
        
    def show_timed_start(self, time_limit):
        """Show timed challenge start message"""
        self.clear_screen()
        print(f"\nTIMED CHALLENGE: Solve as many problems as you can in {time_limit} seconds!")
        print("Press Enter to start...")
        input()
        
    def show_timed_summary(self, stats):
        """Show timed challenge summary"""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("              TIMED CHALLENGE RESULTS              ")
        print("=" * 60)
        
        print(f"Problems attempted: {stats['total_rounds']}")
        print(f"Correctly solved: {stats['correct_count']}")
        print(f"Accuracy: {stats['accuracy']:.1f}%")
        print(f"Average time per problem: {stats['avg_time']:.2f} seconds")
        print(f"Total score: {stats['total_score']}")
        print("=" * 60)
        
        print("\nPress Enter to return to the main menu...")
        input()
        
    def show_pythonista_tips(self):
        """Show Pythonista-specific tips if relevant"""
        if IS_PYTHONISTA:
            print("\nPYTHONISTA TIPS:")
            print("- Use the numeric keyboard for faster input")
            print("- Try landscape mode for a better view")
            print("- Tap the editor to hide this game and resume later\n")
            time.sleep(2)
