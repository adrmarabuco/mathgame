#!/usr/bin/env python3

import random
from datetime import datetime
import time

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


class MathGame:
    """
    Core class for the MathMaster game logic
    """
    def __init__(self):
        self.operation_type = None
        self.difficulty = 1
        self.adaptive_difficulty = False
        self.rounds = MAX_ROUNDS
        self.results = []
        self.streak_count = 0
        self.total_score = 0
        self.timed_mode = False
        self.time_limit = 60  # Default 60 seconds for timed mode
        
    def setup_game(self, operation_type, difficulty_choice, rounds=MAX_ROUNDS, timed_mode=False, time_limit=60):
        """
        Set up game parameters
        """
        self.operation_type = operation_type
        self.rounds = rounds
        self.results = []
        self.streak_count = 0
        self.total_score = 0
        self.timed_mode = timed_mode
        self.time_limit = time_limit
        
        # Set difficulty level based on choice
        if difficulty_choice < 4:
            self.difficulty = difficulty_choice
            self.adaptive_difficulty = False
        else:
            self.difficulty = 1  # Start with easy
            self.adaptive_difficulty = True
    
    def generate_question(self, question_module):
        """
        Generate a question using the question_module based on operation type and difficulty
        """
        return question_module.generate_question(self.operation_type, self.difficulty)
    
    def calculate_score(self, is_correct, time_taken):
        """
        Calculate score based on correctness, time, and difficulty
        """
        if not is_correct:
            return 0
        
        # Base score for correct answer
        score = POINTS_BASE * POINTS_DIFFICULTY_MULTIPLIER[self.difficulty - 1]
        
        # Speed bonus for quick answers
        if time_taken < POINTS_SPEED_BONUS_THRESHOLD:
            speed_factor = max(0, (POINTS_SPEED_BONUS_THRESHOLD - time_taken) / POINTS_SPEED_BONUS_THRESHOLD)
            score += POINTS_SPEED_BONUS * speed_factor
        
        # Streak bonus
        if self.streak_count >= STREAK_BONUS_THRESHOLD:
            score += STREAK_BONUS * (1 + (self.streak_count - STREAK_BONUS_THRESHOLD) * 0.1)
        
        return int(score)
    
    def adjust_difficulty(self):
        """
        Adjust difficulty based on recent performance if adaptive mode is on
        """
        if not self.adaptive_difficulty:
            return None  # No change
            
        # Get the last 3 rounds or fewer if not enough
        recent_results = self.results[-3:]
        if len(recent_results) < 3:
            return None  # Not enough data
            
        correct_count = sum(1 for r in recent_results if r['correct'])
        avg_time = sum(r['time_taken'] for r in recent_results) / len(recent_results)
        
        old_difficulty = self.difficulty
        
        # Adjust difficulty based on performance
        if correct_count == 3 and avg_time < 5.0:  # All correct and fast
            self.difficulty = min(3, self.difficulty + 1)  # Increase difficulty (max 3)
        elif correct_count <= 1:  # Poor performance
            self.difficulty = max(1, self.difficulty - 1)  # Decrease difficulty (min 1)
            
        # Return message if difficulty changed
        if old_difficulty != self.difficulty:
            difficulty_names = ['Easy', 'Medium', 'Hard']
            if self.difficulty > old_difficulty:
                return f"Difficulty increased to {difficulty_names[self.difficulty-1]}"
            else:
                return f"Difficulty adjusted to {difficulty_names[self.difficulty-1]} to help you improve"
        
        return None  # No change
    
    def update_streak(self, is_correct):
        """
        Update the streak counter based on the result
        """
        streak_message = None
        
        if is_correct:
            self.streak_count += 1
            if self.streak_count >= STREAK_BONUS_THRESHOLD and self.streak_count % STREAK_BONUS_THRESHOLD == 0:
                streak_message = f"{self.streak_count} ANSWER STREAK!"
        else:
            # Reset streak on wrong answer
            if self.streak_count >= STREAK_BONUS_THRESHOLD:
                streak_message = "Streak broken!"
            self.streak_count = 0
            
        return streak_message
    
    def get_game_stats(self):
        """
        Calculate and return game statistics
        """
        if not self.results:
            return {
                'total_rounds': 0,
                'correct_count': 0,
                'accuracy': 0,
                'avg_time': 0,
                'total_score': 0
            }
            
        total_rounds = len(self.results)
        correct_count = sum(1 for r in self.results if r['correct'])
        accuracy = (correct_count / total_rounds) * 100 if total_rounds > 0 else 0
        avg_time = sum(r['time_taken'] for r in self.results) / total_rounds if total_rounds > 0 else 0
        total_score = sum(r.get('score', 0) for r in self.results)
        
        return {
            'total_rounds': total_rounds,
            'correct_count': correct_count,
            'accuracy': accuracy,
            'avg_time': avg_time,
            'total_score': total_score
        }
    
    def add_result(self, round_result):
        """
        Add a round result to the results list
        """
        self.results.append(round_result)
        self.total_score += round_result.get('score', 0)
        
    def play_timed_challenge(self, ui_handler, question_module):
        """
        Play a timed challenge where the player solves as many problems as possible
        within a time limit
        """
        # Reset results for this session
        self.results = []
        self.streak_count = 0
        self.total_score = 0
        
        start_time = time.time()
        end_time = start_time + self.time_limit
        round_num = 1
        
        ui_handler.show_timed_start(self.time_limit)
        
        while time.time() < end_time:
            # Calculate remaining time
            remaining_time = max(0, end_time - time.time())
            
            # Generate question
            question, correct_answer = self.generate_question(question_module)
            
            # Get user input with time tracking
            round_start = datetime.now()
            user_answer, input_time_taken = ui_handler.get_answer_timed(
                question, round_num, remaining_time
            )
            round_end = datetime.now()
            
            # If time's up or user quit
            if user_answer == "__TIME_UP__" or user_answer == "__QUIT__":
                break
                
            time_taken = (round_end - round_start).total_seconds()
            
            # Check answer and calculate score
            is_correct = self.check_answer(user_answer, correct_answer)
            score = self.calculate_score(is_correct, time_taken)
            
            # Create result and add to results
            result = {
                'correct': is_correct,
                'time_taken': time_taken,
                'question': question,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'score': score
            }
            self.add_result(result)
            
            # Update streak
            streak_message = self.update_streak(is_correct)
            
            # Show result
            ui_handler.show_round_result(result, score, streak_message)
            
            # Adjust difficulty if adaptive mode is on
            if self.adaptive_difficulty and round_num % 3 == 0:
                difficulty_message = self.adjust_difficulty()
                if difficulty_message:
                    ui_handler.show_difficulty_change(difficulty_message)
            
            round_num += 1
        
        # Show final results
        ui_handler.show_timed_summary(self.get_game_stats())
        return self.get_game_stats()
    
    def check_answer(self, user_answer, correct_answer):
        """
        Check if the user's answer is correct
        """
        if user_answer is None:
            return False
            
        # Convert answers to strings for comparison
        user_str = str(user_answer).strip()
        correct_str = str(correct_answer).strip()
        
        # Direct string comparison first (handles exact matches)
        if user_str == correct_str:
            return True
            
        # Try to normalize fractions for comparison
        try:
            import fractions
            
            # Convert both to fractions if possible
            if '/' in user_str and '/' in correct_str:
                user_parts = user_str.split('/')
                correct_parts = correct_str.split('/')
                
                if len(user_parts) == 2 and len(correct_parts) == 2:
                    try:
                        user_frac = fractions.Fraction(int(user_parts[0]), int(user_parts[1]))
                        correct_frac = fractions.Fraction(int(correct_parts[0]), int(correct_parts[1]))
                        return user_frac == correct_frac
                    except (ValueError, ZeroDivisionError):
                        pass  # Fall through to other methods if fraction conversion fails
            
            # Try creating fractions from any numeric format
            try:
                # Try to convert user answer to Fraction regardless of format
                if '/' in user_str:
                    user_frac = fractions.Fraction(user_str)
                else:
                    user_frac = fractions.Fraction(float(user_str))
                    
                # Try to convert correct answer to Fraction regardless of format
                if '/' in correct_str:
                    correct_frac = fractions.Fraction(correct_str)
                else:
                    correct_frac = fractions.Fraction(float(correct_str))
                    
                return user_frac == correct_frac
            except (ValueError, ZeroDivisionError):
                pass  # Fall through to float comparison
            
            # Handle float comparisons with small tolerance
            try:
                user_float = float(user_str) if '/' not in user_str else float(user_parts[0]) / float(user_parts[1])
                correct_float = float(correct_str) if '/' not in correct_str else float(correct_parts[0]) / float(correct_parts[1])
                # Allow small tolerance for floating point
                return abs(user_float - correct_float) < 0.001
            except (ValueError, ZeroDivisionError):
                pass  # Fall through to final direct comparison
                
        except Exception as e:
            # If any unexpected error occurs, log it and continue to direct comparison
            print(f"Error comparing answers: {e}")
            
        # Final fallback: direct string comparison
        return user_str == correct_str
