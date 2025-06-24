#!/usr/bin/env python3

import os
import json
import time
from questions import QuestionGenerator

class HighScoreManager:
    """
    Class to handle high score tracking and persistence
    """
    def __init__(self):
        self.scores_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'high_scores.json')
        self.scores = self._load_scores()
        
    def _load_scores(self):
        """Load scores from file if it exists, otherwise create new"""
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print("Error loading high scores file. Creating new one.")
                return self._create_default_scores()
        else:
            return self._create_default_scores()
    
    def _create_default_scores(self):
        """Create default empty scores structure"""
        scores = {
            "normal_mode": {},
            "timed_mode": {},
            "last_played": {},
            "stats": {
                "total_problems_solved": 0,
                "total_time_played": 0,
                "games_played": 0
            }
        }
        
        # Initialize scores for each operation and difficulty
        for mode in ["normal_mode", "timed_mode"]:
            for op in range(1, 10):  # 1-9 operation types
                op_name = QuestionGenerator.get_operation_name(op).lower().replace(" ", "_")
                scores[mode][op_name] = {}
                for diff in range(1, 4):  # 1-3 difficulty levels
                    scores[mode][op_name][f"difficulty_{diff}"] = {
                        "score": 0,
                        "date": "",
                        "accuracy": 0,
                        "avg_time": 0
                    }
                    
        return scores
    
    def _save_scores(self):
        """Save scores to file"""
        try:
            with open(self.scores_file, 'w') as f:
                json.dump(self.scores, f, indent=2)
                return True
        except IOError:
            print("Error saving high scores.")
            return False
    
    def update_high_score(self, game_mode, operation_type, difficulty, stats):
        """
        Update high score if current score is higher
        
        Args:
            game_mode: 'normal_mode' or 'timed_mode'
            operation_type: Operation type number (1-9)
            difficulty: Difficulty level (1-3)
            stats: Game statistics dictionary
            
        Returns:
            Tuple of (is_high_score, previous_high_score) or None if error
        """
        if game_mode not in ["normal_mode", "timed_mode"]:
            return None
            
        # Get operation name (e.g., "addition")
        op_name = QuestionGenerator.get_operation_name(operation_type).lower().replace(" ", "_")
        
        # Ensure adaptive difficulty is mapped to an actual difficulty (1-3)
        if difficulty > 3:
            difficulty = stats.get('average_difficulty', 1)
            
        diff_key = f"difficulty_{difficulty}"
            
        # Ensure structure exists
        if op_name not in self.scores[game_mode]:
            self.scores[game_mode][op_name] = {}
            
        if diff_key not in self.scores[game_mode][op_name]:
            self.scores[game_mode][op_name][diff_key] = {
                "score": 0, 
                "date": "", 
                "accuracy": 0,
                "avg_time": 0
            }
            
        # Check if new score is higher
        prev_high_score = self.scores[game_mode][op_name][diff_key]["score"]
        is_high_score = stats["total_score"] > prev_high_score
        
        if is_high_score:
            # Update high score
            self.scores[game_mode][op_name][diff_key] = {
                "score": stats["total_score"],
                "date": time.strftime("%Y-%m-%d %H:%M"),
                "accuracy": stats["accuracy"],
                "avg_time": stats["avg_time"]
            }
            
            # Save to file
            self._save_scores()
            
        # Update last played and stats
        self.scores["last_played"] = {
            "operation": op_name,
            "difficulty": difficulty,
            "mode": game_mode,
            "date": time.strftime("%Y-%m-%d %H:%M")
        }
        
        self.scores["stats"]["total_problems_solved"] += stats["total_rounds"]
        self.scores["stats"]["total_time_played"] += stats["avg_time"] * stats["total_rounds"]
        self.scores["stats"]["games_played"] += 1
        
        # Save updates
        self._save_scores()
        
        return (is_high_score, prev_high_score)
        
    def get_high_score(self, game_mode, operation_type, difficulty):
        """Get high score for specified parameters"""
        try:
            op_name = QuestionGenerator.get_operation_name(operation_type).lower().replace(" ", "_")
            diff_key = f"difficulty_{min(difficulty, 3)}"
            return self.scores[game_mode][op_name][diff_key]
        except KeyError:
            return {"score": 0, "date": "", "accuracy": 0, "avg_time": 0}
            
    def get_all_high_scores(self):
        """Get all high scores"""
        return self.scores
        
    def get_stats(self):
        """Get overall statistics"""
        return self.scores["stats"]
        
    def display_high_scores(self, cli, game_mode=None, operation_type=None):
        """
        Display high scores in CLI
        
        Args:
            cli: CLI interface object
            game_mode: Mode to filter by (optional)
            operation_type: Operation to filter by (optional)
        """
        cli.clear_screen()
        print("\n" + "=" * 60)
        print("                   HIGH SCORES                   ")
        print("=" * 60)
        
        modes = ["normal_mode", "timed_mode"] if not game_mode else [game_mode]
        
        for mode in modes:
            mode_display = "NORMAL MODE" if mode == "normal_mode" else "TIMED MODE"
            print(f"\n{mode_display}")
            print("-" * len(mode_display))
            
            for op_num in range(1, 10):
                if operation_type and op_num != operation_type:
                    continue
                    
                op_name = QuestionGenerator.get_operation_name(op_num)
                op_key = op_name.lower().replace(" ", "_")
                
                if op_key in self.scores[mode]:
                    print(f"\n{op_name}:")
                    for diff in range(1, 4):
                        diff_key = f"difficulty_{diff}"
                        diff_name = ["Easy", "Medium", "Hard"][diff-1]
                        
                        if diff_key in self.scores[mode][op_key]:
                            score_data = self.scores[mode][op_key][diff_key]
                            if score_data["score"] > 0:
                                print(f"  {diff_name}: {score_data['score']} points " + 
                                      f"(Accuracy: {score_data['accuracy']:.1f}%, " + 
                                      f"Avg Time: {score_data['avg_time']:.2f}s, " + 
                                      f"Date: {score_data['date']})")
                            else:
                                print(f"  {diff_name}: No score yet")
        
        # Display overall statistics
        print("\n" + "=" * 60)
        print("OVERALL STATS")
        print(f"Total problems solved: {self.scores['stats']['total_problems_solved']}")
        print(f"Total time played: {self.scores['stats']['total_time_played'] / 60:.1f} minutes")
        print(f"Games played: {self.scores['stats']['games_played']}")
        
        if self.scores['last_played']:
            last = self.scores['last_played']
            print(f"\nLast played: {last['operation'].replace('_', ' ').title()} " + 
                  f"(Difficulty {last['difficulty']}) in {last['mode'].replace('_', ' ').title()} " + 
                  f"on {last['date']}")
        
        print("\nPress Enter to continue...")
        input()
