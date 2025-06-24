#!/usr/bin/env python3

"""
Touch-friendly UI for MathMaster using Pythonista's UI module
This provides an alternative interface for iOS users
"""

try:
    import ui
    import console
    from objc_util import ObjCInstance
    PYTHONISTA_AVAILABLE = True
except ImportError:
    PYTHONISTA_AVAILABLE = False
    print("Pythonista UI modules not available. This module requires Pythonista on iOS.")
    
import time
from datetime import datetime
import threading
from questions import QuestionGenerator, OPERATION_MIXED
from game import MathGame
from high_scores import HighScoreManager

# Constants
TINT_COLOR = '#007aff'  # iOS blue tint color
BACKGROUND_COLOR = '#f8f8f8'  # Light background
CORRECT_COLOR = '#34c759'  # iOS green
INCORRECT_COLOR = '#ff3b30'  # iOS red
LIGHT_GRAY = '#e5e5ea'  # iOS light gray

class MathGameUI:
    """Touch-friendly UI for the MathMaster game using Pythonista UI"""
    
    def __init__(self):
        """Initialize the UI components and game state"""
        # Always create these elements regardless of environment
        self.game = MathGame()
        self.high_scores = HighScoreManager()
        self.question_module = QuestionGenerator
        
        # Game state variables
        self.current_question = None
        self.correct_answer = None
        self.round_start_time = None
        self.round_num = 1
        self.operation_type = 1  # Default to addition
        self.difficulty = 1      # Default to easy
        
        # Early exit if not in Pythonista environment
        # The global PYTHONISTA_AVAILABLE flag is already set at module level
        if not PYTHONISTA_AVAILABLE:
            return
        
        # Pythonista-specific UI initialization
        self.current_view = None
        self.timer = None
        self.timer_running = False
        self.countdown_seconds = 0
        
        # Create root view for navigation
        root_view = ui.View()
        root_view.name = 'MathMaster'
        root_view.background_color = BACKGROUND_COLOR
        
        # Setup main navigation with the root view
        self.nav_view = ui.NavigationView(root_view)
        self.nav_view.name = 'MathMaster'
        self.nav_view.background_color = BACKGROUND_COLOR
        self.nav_view.tint_color = TINT_COLOR
        
        # Create main menu
        self.setup_main_menu()
    
    def setup_main_menu(self):
        """Setup the main menu view"""
        main_view = ui.View()
        main_view.name = 'MathMaster'
        main_view.background_color = BACKGROUND_COLOR
        
        # Title label
        title_label = ui.Label(frame=(0, 50, 500, 50))
        title_label.text = 'MathMaster'
        title_label.alignment = ui.ALIGN_CENTER
        title_label.font = ('Helvetica-Bold', 28)
        title_label.text_color = TINT_COLOR
        title_label.center = (main_view.width * 0.5, 80)
        title_label.flex = 'WLRTB'
        main_view.add_subview(title_label)
        
        # Subtitle
        subtitle = ui.Label(frame=(0, 110, 500, 30))
        subtitle.text = 'Improve your math skills with practice'
        subtitle.alignment = ui.ALIGN_CENTER
        subtitle.font = ('Helvetica', 16)
        subtitle.center = (main_view.width * 0.5, 120)
        subtitle.flex = 'WLRTB'
        main_view.add_subview(subtitle)
        
        # Create menu buttons
        y_offset = 180
        button_width = 200
        button_height = 50
        
        operations_btn = self.create_button('Practice Operations', 
                                      frame=(0, y_offset, button_width, button_height),
                                      action=self.show_operations)
        operations_btn.center = (main_view.width * 0.5, y_offset + button_height/2)
        operations_btn.flex = 'LR'
        main_view.add_subview(operations_btn)
        
        y_offset += 70
        timed_btn = self.create_button('Timed Challenge', 
                                  frame=(0, y_offset, button_width, button_height),
                                  action=self.show_timed_setup)
        timed_btn.center = (main_view.width * 0.5, y_offset + button_height/2)
        timed_btn.flex = 'LR'
        main_view.add_subview(timed_btn)
        
        y_offset += 70
        scores_btn = self.create_button('High Scores', 
                                   frame=(0, y_offset, button_width, button_height),
                                   action=self.show_high_scores)
        scores_btn.center = (main_view.width * 0.5, y_offset + button_height/2)
        scores_btn.flex = 'LR'
        main_view.add_subview(scores_btn)
        
        y_offset += 70
        settings_btn = self.create_button('About', 
                                    frame=(0, y_offset, button_width, button_height),
                                    action=self.show_about)
        settings_btn.center = (main_view.width * 0.5, y_offset + button_height/2)
        settings_btn.flex = 'LR'
        main_view.add_subview(settings_btn)
        
        # Set the main view
        self.current_view = main_view
        self.nav_view.push_view(main_view)
    
    def create_button(self, title, frame=(0, 0, 200, 50), action=None):
        """Helper to create a styled button"""
        button = ui.Button(frame=frame)
        button.title = title
        button.tint_color = 'white'
        button.background_color = TINT_COLOR
        button.corner_radius = 10
        button.action = action
        return button
    
    def show_operations(self, sender):
        """Show the operations selection menu"""
        op_view = ui.View()
        op_view.name = 'Select Operation'
        op_view.background_color = BACKGROUND_COLOR
        
        # Create operation buttons
        operations = {
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
        
        # Instructions
        instructions = ui.Label(frame=(0, 50, 500, 30))
        instructions.text = 'Select an operation to practice:'
        instructions.alignment = ui.ALIGN_CENTER
        instructions.font = ('Helvetica-Bold', 18)
        instructions.center = (op_view.width * 0.5, 50)
        instructions.flex = 'WLRTB'
        op_view.add_subview(instructions)
        
        # Create a button for each operation
        y_offset = 100
        button_height = 50
        button_width = 250
        button_spacing = 15
        
        for op_id, op_name in operations.items():
            btn = self.create_button(op_name, 
                               frame=(0, y_offset, button_width, button_height))
            btn.center = (op_view.width * 0.5, y_offset + button_height/2)
            btn.flex = 'LR'
            
            # Store operation ID in button's name for reference in handler
            btn.name = str(op_id)
            btn.action = self.operation_selected
            
            op_view.add_subview(btn)
            y_offset += button_height + button_spacing
        
        self.nav_view.push_view(op_view)
    
    def operation_selected(self, sender):
        """Handle operation selection"""
        self.operation_type = int(sender.name)
        self.show_difficulty()
    
    def show_difficulty(self):
        """Show the difficulty selection menu"""
        diff_view = ui.View()
        diff_view.name = 'Select Difficulty'
        diff_view.background_color = BACKGROUND_COLOR
        
        # Create difficulty options
        difficulties = {
            1: "Easy",
            2: "Medium",
            3: "Hard",
            4: "Adaptive"
        }
        
        # Instructions
        op_name = self.question_module.get_operation_name(self.operation_type)
        instructions = ui.Label(frame=(0, 50, 500, 30))
        instructions.text = f'Select difficulty for {op_name}:'
        instructions.alignment = ui.ALIGN_CENTER
        instructions.font = ('Helvetica-Bold', 18)
        instructions.center = (diff_view.width * 0.5, 50)
        instructions.flex = 'WLRTB'
        diff_view.add_subview(instructions)
        
        # Create a button for each difficulty
        y_offset = 100
        button_height = 50
        button_width = 250
        button_spacing = 20
        
        for diff_id, diff_name in difficulties.items():
            btn = self.create_button(diff_name, 
                               frame=(0, y_offset, button_width, button_height))
            btn.center = (diff_view.width * 0.5, y_offset + button_height/2)
            btn.flex = 'LR'
            
            # Store difficulty ID in button's name for reference in handler
            btn.name = str(diff_id)
            btn.action = self.difficulty_selected
            
            diff_view.add_subview(btn)
            y_offset += button_height + button_spacing
        
        self.nav_view.push_view(diff_view)
    
    def difficulty_selected(self, sender):
        """Handle difficulty selection"""
        self.difficulty = int(sender.name)
        self.show_rounds_selection()
    
    def show_rounds_selection(self):
        """Show the rounds selection view"""
        rounds_view = ui.View()
        rounds_view.name = 'Number of Rounds'
        rounds_view.background_color = BACKGROUND_COLOR
        
        # Instructions
        instructions = ui.Label(frame=(0, 50, 500, 30))
        instructions.text = 'How many rounds?'
        instructions.alignment = ui.ALIGN_CENTER
        instructions.font = ('Helvetica-Bold', 18)
        instructions.center = (rounds_view.width * 0.5, 50)
        instructions.flex = 'WLRTB'
        rounds_view.add_subview(instructions)
        
        # Round number options
        round_options = [5, 10, 15, 20]
        
        # Create a button for each option
        y_offset = 100
        button_height = 50
        button_width = 250
        button_spacing = 20
        
        for rounds in round_options:
            btn = self.create_button(f"{rounds} Rounds", 
                              frame=(0, y_offset, button_width, button_height))
            btn.center = (rounds_view.width * 0.5, y_offset + button_height/2)
            btn.flex = 'LR'
            
            # Store round count in button's name
            btn.name = str(rounds)
            btn.action = self.rounds_selected
            
            rounds_view.add_subview(btn)
            y_offset += button_height + button_spacing
        
        self.nav_view.push_view(rounds_view)
    
    def rounds_selected(self, sender):
        """Handle rounds selection and start game"""
        rounds = int(sender.name)
        
        # Set up game
        self.game.setup_game(
            operation_type=self.operation_type,
            difficulty_choice=self.difficulty,
            rounds=rounds
        )
        
        # Reset round counter
        self.round_num = 1
        
        # Start first question
        self.show_game_screen()
    
    def show_game_screen(self):
        """Display the game screen with question"""
        game_view = ui.View()
        game_view.name = 'MathMaster'
        game_view.background_color = BACKGROUND_COLOR
        
        # Generate question
        question_data = self.game.generate_question()
        self.current_question = question_data[0]
        self.correct_answer = question_data[1]
        
        # Update round counter
        self.round_num = self.game.current_round
        
        # Record start time
        self.round_start_time = datetime.now()
        
        # Round info label
        round_label = ui.Label(frame=(0, 30, 500, 30))
        round_label.text = f'Round {self.round_num} of {self.game.total_rounds}'
        round_label.alignment = ui.ALIGN_CENTER
        round_label.font = ('Helvetica', 16)
        round_label.center = (game_view.width * 0.5, 45)
        round_label.flex = 'WLRTB'
        game_view.add_subview(round_label)
        
        # Question label
        question_label = ui.Label(frame=(0, 90, 500, 50))
        question_label.text = f'Calculate: {self.current_question}'
        question_label.alignment = ui.ALIGN_CENTER
        question_label.font = ('Helvetica-Bold', 24)
        question_label.center = (game_view.width * 0.5, 110)
        question_label.flex = 'WLRTB'
        game_view.add_subview(question_label)
        
        # Answer field
        answer_field = ui.TextField(frame=(0, 180, 200, 40))
        answer_field.placeholder = 'Enter your answer'
        answer_field.alignment = ui.ALIGN_CENTER
        answer_field.keyboard_type = ui.KEYBOARD_NUMBERS
        answer_field.clear_button_mode = 'while_editing'
        answer_field.autocorrection_type = False
        answer_field.spellchecking_type = False
        answer_field.font = ('Helvetica', 20)
        answer_field.center = (game_view.width * 0.5, 200)
        answer_field.flex = 'LR'
        answer_field.border_width = 1
        answer_field.corner_radius = 5
        answer_field.border_color = LIGHT_GRAY
        game_view.add_subview(answer_field)
        
        # Timer label (updating)
        timer_label = ui.Label(frame=(0, 240, 500, 30))
        timer_label.text = f'Time: 0.0s'
        timer_label.alignment = ui.ALIGN_CENTER
        timer_label.font = ('Helvetica', 16)
        timer_label.text_color = 'gray'
        timer_label.center = (game_view.width * 0.5, 255)
        timer_label.flex = 'WLRTB'
        timer_label.name = 'timer_label'
        game_view.add_subview(timer_label)
        
        # Submit button
        submit_btn = self.create_button('Submit', 
                                  frame=(0, 300, 200, 50),
                                  action=self.check_answer)
        submit_btn.center = (game_view.width * 0.5, 325)
        submit_btn.flex = 'LR'
        # Store reference to the answer field for use in the handler
        submit_btn.name = 'answer_submit'
        submit_btn.answer_field = answer_field
        game_view.add_subview(submit_btn)
        
        # Start timer update
        self.start_timer_update(game_view, timer_label)
        
        # Set focus to the answer field for immediate typing
        answer_field.begin_editing()
        
        # Replace the current view with the game view
        self.nav_view.push_view(game_view)
    
    def start_timer_update(self, view, timer_label):
        """Start a timer to update the elapsed time display"""
        def update_timer():
            elapsed = (datetime.now() - self.round_start_time).total_seconds()
            timer_label.text = f'Time: {elapsed:.1f}s'
            if view.on_screen:
                ui.delay(update_timer, 0.1)
        
        ui.delay(update_timer, 0.1)
    
    def check_answer(self, sender):
        """Check the provided answer and show feedback"""
        # Get the answer from the text field
        answer_field = sender.answer_field
        user_answer = answer_field.text.strip()
        
        # Calculate time taken
        time_taken = (datetime.now() - self.round_start_time).total_seconds()
        
        # Check answer and get result
        result = self.game.check_answer(user_answer, time_taken)
        
        # Display result
        self.show_answer_result(result)
    
    def show_answer_result(self, result):
        """Display the result of the answer check"""
        result_view = ui.View()
        result_view.background_color = BACKGROUND_COLOR
        
        # Status icon and color
        status_text = '✓' if result['correct'] else '✗'
        status_color = CORRECT_COLOR if result['correct'] else INCORRECT_COLOR
        
        # Large status indicator
        status_label = ui.Label(frame=(0, 80, 200, 100))
        status_label.text = status_text
        status_label.alignment = ui.ALIGN_CENTER
        status_label.font = ('Helvetica-Bold', 80)
        status_label.text_color = status_color
        status_label.center = (result_view.width * 0.5, 130)
        status_label.flex = 'WLRTB'
        result_view.add_subview(status_label)
        
        # Result text
        if result['correct']:
            result_text = f"Correct! +{result['score']} points"
        else:
            result_text = f"Incorrect. The answer was {result['correct_answer']}"
        
        result_label = ui.Label(frame=(0, 200, 300, 40))
        result_label.text = result_text
        result_label.alignment = ui.ALIGN_CENTER
        result_label.font = ('Helvetica', 18)
        result_label.center = (result_view.width * 0.5, 220)
        result_label.flex = 'WLRTB'
        result_view.add_subview(result_label)
        
        # Time info
        time_label = ui.Label(frame=(0, 240, 300, 30))
        time_label.text = f"Time: {result['time_taken']:.2f} seconds"
        time_label.alignment = ui.ALIGN_CENTER
        time_label.font = ('Helvetica', 16)
        time_label.center = (result_view.width * 0.5, 260)
        time_label.flex = 'WLRTB'
        result_view.add_subview(time_label)
        
        # Streak info if available
        if 'streak' in result:
            streak_label = ui.Label(frame=(0, 280, 300, 30))
            streak_label.text = f"Current streak: {result['streak']}"
            streak_label.alignment = ui.ALIGN_CENTER
            streak_label.font = ('Helvetica', 16)
            streak_label.center = (result_view.width * 0.5, 290)
            streak_label.flex = 'WLRTB'
            result_view.add_subview(streak_label)
        
        # Continue button
        if self.game.current_round <= self.game.total_rounds:
            continue_btn = self.create_button('Next Question', 
                                      frame=(0, 320, 200, 50),
                                      action=self.show_game_screen)
        else:
            continue_btn = self.create_button('See Results', 
                                      frame=(0, 320, 200, 50),
                                      action=self.show_game_summary)
        
        continue_btn.center = (result_view.width * 0.5, 345)
        continue_btn.flex = 'LR'
        result_view.add_subview(continue_btn)
        
        self.nav_view.push_view(result_view)
    
    def show_game_summary(self, sender=None):
        """Display game summary and stats"""
        summary_view = ui.View()
        summary_view.name = 'Game Summary'
        summary_view.background_color = BACKGROUND_COLOR
        
        # Get game results
        results = self.game.get_results()
        
        # Calculate stats
        total_rounds = len(results)
        correct_count = sum(1 for r in results if r['correct'])
        accuracy = (correct_count / total_rounds) * 100 if total_rounds > 0 else 0
        avg_time = sum(r['time_taken'] for r in results) / total_rounds if total_rounds > 0 else 0
        total_score = sum(r.get('score', 0) for r in results)
        
        # Title
        title_label = ui.Label(frame=(0, 30, 500, 40))
        title_label.text = 'Game Summary'
        title_label.alignment = ui.ALIGN_CENTER
        title_label.font = ('Helvetica-Bold', 24)
        title_label.center = (summary_view.width * 0.5, 50)
        title_label.flex = 'WLRTB'
        summary_view.add_subview(title_label)
        
        # Stats container
        stats_view = ui.View(frame=(0, 90, 300, 160))
        stats_view.border_width = 1
        stats_view.border_color = LIGHT_GRAY
        stats_view.corner_radius = 10
        stats_view.center = (summary_view.width * 0.5, 170)
        stats_view.flex = 'LR'
        
        # Stats labels
        y_pos = 15
        font_size = 16
        line_height = 30
        
        stats_labels = [
            f"Total Questions: {total_rounds}",
            f"Correct Answers: {correct_count}",
            f"Accuracy: {accuracy:.1f}%",
            f"Average Time: {avg_time:.2f}s",
            f"Total Score: {total_score} points"
        ]
        
        for text in stats_labels:
            label = ui.Label(frame=(20, y_pos, 260, line_height))
            label.text = text
            label.font = ('Helvetica', font_size)
            stats_view.add_subview(label)
            y_pos += line_height
        
        summary_view.add_subview(stats_view)
        
        # Action buttons
        y_offset = 280
        button_width = 200
        button_height = 50
        button_spacing = 20
        
        # Save score button
        save_btn = self.create_button('Save Score', 
                               frame=(0, y_offset, button_width, button_height),
                               action=self.save_high_score)
        save_btn.center = (summary_view.width * 0.5, y_offset + button_height/2)
        save_btn.flex = 'LR'
        summary_view.add_subview(save_btn)
        
        # Main menu button
        y_offset += button_height + button_spacing
        menu_btn = self.create_button('Main Menu', 
                               frame=(0, y_offset, button_width, button_height),
                               action=self.return_to_main_menu)
        menu_btn.center = (summary_view.width * 0.5, y_offset + button_height/2)
        menu_btn.flex = 'LR'
        summary_view.add_subview(menu_btn)
        
        # Save high score on game completion
        op_name = self.question_module.get_operation_name(self.operation_type)
        diff_name = "Adaptive" if self.difficulty == 4 else f"Level {self.difficulty}"
        
        # Save the high score
        self.game_stats = {
            'total_rounds': total_rounds,
            'correct_count': correct_count,
            'accuracy': accuracy,
            'avg_time': avg_time,
            'total_score': total_score,
            'operation': op_name,
            'difficulty': diff_name,
            'timed_mode': False
        }
        
        self.nav_view.push_view(summary_view)
    
    def save_high_score(self, sender):
        """Save the current score to high scores"""
        if hasattr(self, 'game_stats'):
            # Format data for high score manager
            score_data = {
                'score': self.game_stats['total_score'],
                'accuracy': self.game_stats['accuracy'],
                'avg_time': self.game_stats['avg_time'],
                'operation': self.game_stats['operation'],
                'difficulty': self.game_stats['difficulty'],
                'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'timed_mode': self.game_stats['timed_mode']
            }
            
            # Save the score
            self.high_scores.add_high_score(score_data)
            
            # Show confirmation
            console.hud_alert('Score saved!', 'success', 1.5)
            
            # Disable the save button to prevent duplicate saves
            sender.enabled = False
            sender.background_color = LIGHT_GRAY
    
    def return_to_main_menu(self, sender):
        """Return to the main menu"""
        # Clear the navigation stack and rebuild main menu
        self.nav_view.close()
        
        # Create root view for navigation
        root_view = ui.View()
        root_view.name = 'MathMaster'
        root_view.background_color = BACKGROUND_COLOR
        
        # Create new navigation view with root view
        self.nav_view = ui.NavigationView(root_view)
        self.nav_view.name = 'MathMaster'
        self.nav_view.background_color = BACKGROUND_COLOR
        self.nav_view.tint_color = TINT_COLOR
        self.setup_main_menu()
        
        # Present the nav view again
        self.nav_view.present('fullscreen')
    
    def show_high_scores(self, sender):
        """Display the high scores screen"""
        hs_view = ui.View()
        hs_view.name = 'High Scores'
        hs_view.background_color = BACKGROUND_COLOR
        
        # Title
        title_label = ui.Label(frame=(0, 30, 500, 40))
        title_label.text = 'High Scores'
        title_label.alignment = ui.ALIGN_CENTER
        title_label.font = ('Helvetica-Bold', 24)
        title_label.center = (hs_view.width * 0.5, 50)
        title_label.flex = 'WLRTB'
        hs_view.add_subview(title_label)
        
        # Get high scores
        normal_scores = self.high_scores.get_high_scores(timed_mode=False)
        timed_scores = self.high_scores.get_high_scores(timed_mode=True)
        
        # Create segmented control for switching between normal/timed
        segments = ui.SegmentedControl(frame=(0, 90, 250, 30))
        segments.segments = ('Practice Mode', 'Timed Mode')
        segments.center = (hs_view.width * 0.5, 105)
        segments.selected_index = 0
        segments.flex = 'LR'
        hs_view.add_subview(segments)
        
        # Create a table for high scores
        table = ui.TableView(frame=(0, 140, 300, 300))
        table.center = (hs_view.width * 0.5, 290)
        table.flex = 'LR'
        table.row_height = 60
        table.border_width = 1
        table.border_color = LIGHT_GRAY
        table.corner_radius = 10
        hs_view.add_subview(table)
        
        # Create data source for the table
        table_data = ui.ListDataSource([])
        
        # Function to update table data based on selected segment
        def update_table(segment):
            if segment.selected_index == 0:
                # Normal mode
                scores = normal_scores
            else:
                # Timed mode
                scores = timed_scores
            
            # Format scores for display
            formatted_scores = []
            for score in scores:
                formatted_scores.append({
                    'title': f"{score['operation']} - {score['difficulty']}",
                    'subtitle': f"Score: {score['score']} | Accuracy: {score['accuracy']:.1f}% | Time: {score['avg_time']:.2f}s",
                    'accessory_type': 'detail_button'
                })
            
            table_data.items = formatted_scores
            table.reload()
        
        # Set initial data
        segments.action = update_table
        update_table(segments)
        
        # Set data source
        table.data_source = table_data
        table.delegate = table_data
        
        # Back button
        back_btn = self.create_button('Back', 
                              frame=(0, 450, 200, 50),
                              action=self.return_to_main_menu)
        back_btn.center = (hs_view.width * 0.5, 475)
        back_btn.flex = 'LR'
        hs_view.add_subview(back_btn)
        
        self.nav_view.push_view(hs_view)
    
    def show_timed_setup(self, sender):
        """Show timed challenge setup screen"""
        timed_view = ui.View()
        timed_view.name = 'Timed Challenge'
        timed_view.background_color = BACKGROUND_COLOR
        
        # Title
        title_label = ui.Label(frame=(0, 30, 500, 40))
        title_label.text = 'Timed Challenge'
        title_label.alignment = ui.ALIGN_CENTER
        title_label.font = ('Helvetica-Bold', 24)
        title_label.center = (timed_view.width * 0.5, 50)
        title_label.flex = 'WLRTB'
        timed_view.add_subview(title_label)
        
        # Description
        desc_label = ui.Label(frame=(0, 80, 320, 60))
        desc_label.text = 'Solve as many questions as you can within the time limit!'
        desc_label.alignment = ui.ALIGN_CENTER
        desc_label.number_of_lines = 0
        desc_label.font = ('Helvetica', 17)
        desc_label.center = (timed_view.width * 0.5, 110)
        desc_label.flex = 'WLRTB'
        timed_view.add_subview(desc_label)
        
        # Operation selection (similar to regular mode)
        operations = {
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
        
        # Operation label
        op_label = ui.Label(frame=(0, 160, 500, 30))
        op_label.text = 'Select operation:'
        op_label.alignment = ui.ALIGN_CENTER
        op_label.font = ('Helvetica-Bold', 18)
        op_label.center = (timed_view.width * 0.5, 175)
        op_label.flex = 'WLRTB'
        timed_view.add_subview(op_label)
        
        # Create picker for operations
        op_picker = ui.PickerView(frame=(0, 200, 300, 100))
        op_picker.center = (timed_view.width * 0.5, 250)
        op_picker.flex = 'LR'
        
        # Setup picker data
        op_items = [op for op in operations.values()]
        
        class PickerDelegate:
            def pickerView_numberOfRowsInComponent_(self, picker_view, component):
                return len(op_items)
            
            def pickerView_titleForRow_forComponent_(self, picker_view, row, component):
                return op_items[row]
        
        op_picker.data_source = PickerDelegate()
        op_picker.delegate = PickerDelegate()
        timed_view.add_subview(op_picker)
        
        # Time limit label
        time_label = ui.Label(frame=(0, 320, 500, 30))
        time_label.text = 'Select time limit:'
        time_label.alignment = ui.ALIGN_CENTER
        time_label.font = ('Helvetica-Bold', 18)
        time_label.center = (timed_view.width * 0.5, 335)
        time_label.flex = 'WLRTB'
        timed_view.add_subview(time_label)
        
        # Time limit buttons
        time_options = [30, 60, 120, 180, 300]  # In seconds
        
        # Create buttons in horizontal layout
        button_width = 60
        button_height = 45
        button_spacing = 10
        total_width = button_width * len(time_options) + button_spacing * (len(time_options) - 1)
        x_offset = (timed_view.width - total_width) / 2
        y_pos = 380
        
        for seconds in time_options:
            if seconds < 60:
                time_text = f"{seconds}s"
            else:
                time_text = f"{seconds//60}m"
                
            time_btn = self.create_button(time_text, 
                                   frame=(x_offset, y_pos, button_width, button_height))
            time_btn.name = str(seconds)
            time_btn.action = self.start_timed_challenge
            time_btn.op_picker = op_picker
            time_btn.op_items = op_items
            timed_view.add_subview(time_btn)
            
            x_offset += button_width + button_spacing
        
        # Back button
        back_btn = self.create_button('Back', 
                              frame=(0, 450, 200, 50),
                              action=self.return_to_main_menu)
        back_btn.center = (timed_view.width * 0.5, 475)
        back_btn.flex = 'LR'
        timed_view.add_subview(back_btn)
        
        self.nav_view.push_view(timed_view)
    
    def start_timed_challenge(self, sender):
        """Start a timed challenge game"""
        # Get operation type from picker
        op_picker = sender.op_picker
        op_items = sender.op_items
        selected_op = op_picker.selected_row(0) + 1  # Operations are 1-indexed
        
        # Get time limit from button
        time_limit = int(sender.name)
        
        # Set up timed game
        self.game.setup_timed_game(
            operation_type=selected_op,
            difficulty_choice=2,  # Medium difficulty for timed challenges
            seconds=time_limit
        )
        
        # Reset game state
        self.round_num = 1
        self.timer_running = True
        self.countdown_seconds = time_limit
        
        # Start the game
        self.show_timed_game_screen()
    
    def show_timed_game_screen(self):
        """Display the timed game screen"""
        game_view = ui.View()
        game_view.name = 'Timed Challenge'
        game_view.background_color = BACKGROUND_COLOR
        
        # Generate question
        question_data = self.game.generate_question()
        self.current_question = question_data[0]
        self.correct_answer = question_data[1]
        
        # Update round counter
        self.round_num = self.game.correct_count + self.game.wrong_count + 1
        
        # Record start time
        self.round_start_time = datetime.now()
        
        # Create timer display
        timer_label = ui.Label(frame=(0, 30, 500, 40))
        timer_label.text = f'Time: {self.countdown_seconds}s'
        timer_label.alignment = ui.ALIGN_CENTER
        timer_label.font = ('Helvetica-Bold', 24)
        timer_label.text_color = TINT_COLOR
        timer_label.center = (game_view.width * 0.5, 50)
        timer_label.flex = 'WLRTB'
        timer_label.name = 'timer_label'  # For referencing in timer update
        game_view.add_subview(timer_label)
        
        # Score display
        score_label = ui.Label(frame=(0, 80, 500, 30))
        score_label.text = f'Score: {self.game.total_score} | Solved: {self.game.correct_count}'
        score_label.alignment = ui.ALIGN_CENTER
        score_label.font = ('Helvetica', 17)
        score_label.center = (game_view.width * 0.5, 95)
        score_label.flex = 'WLRTB'
        score_label.name = 'score_label'  # For referencing in updates
        game_view.add_subview(score_label)
        
        # Question label
        question_label = ui.Label(frame=(0, 140, 500, 50))
        question_label.text = f'Calculate: {self.current_question}'
        question_label.alignment = ui.ALIGN_CENTER
        question_label.font = ('Helvetica-Bold', 24)
        question_label.center = (game_view.width * 0.5, 165)
        question_label.flex = 'WLRTB'
        game_view.add_subview(question_label)
        
        # Answer field
        answer_field = ui.TextField(frame=(0, 220, 200, 40))
        answer_field.placeholder = 'Enter your answer'
        answer_field.alignment = ui.ALIGN_CENTER
        answer_field.keyboard_type = ui.KEYBOARD_NUMBERS
        answer_field.clear_button_mode = 'while_editing'
        answer_field.autocorrection_type = False
        answer_field.spellchecking_type = False
        answer_field.font = ('Helvetica', 20)
        answer_field.center = (game_view.width * 0.5, 240)
        answer_field.flex = 'LR'
        answer_field.border_width = 1
        answer_field.corner_radius = 5
        answer_field.border_color = LIGHT_GRAY
        game_view.add_subview(answer_field)
        
        # Submit button
        submit_btn = self.create_button('Submit', 
                                  frame=(0, 290, 200, 50),
                                  action=self.check_timed_answer)
        submit_btn.center = (game_view.width * 0.5, 315)
        submit_btn.flex = 'LR'
        submit_btn.name = 'answer_submit'
        submit_btn.answer_field = answer_field
        game_view.add_subview(submit_btn)
        
        # Start timer countdown
        self.start_countdown(game_view, timer_label, score_label)
        
        # Set focus to the answer field for immediate typing
        answer_field.begin_editing()
        
        # Push the view
        self.nav_view.push_view(game_view)
    
    def start_countdown(self, view, timer_label, score_label):
        """Start countdown timer for timed mode"""
        def update_timer():
            if not view.on_screen or not self.timer_running:
                return
                
            if self.countdown_seconds <= 0:
                # Time's up
                self.timer_running = False
                self.show_timed_summary()
                return
            
            # Update timer
            self.countdown_seconds -= 1
            timer_label.text = f'Time: {self.countdown_seconds}s'
            
            # Change color when time is low
            if self.countdown_seconds <= 10:
                timer_label.text_color = INCORRECT_COLOR
            
            # Schedule next update
            ui.delay(update_timer, 1)
        
        # Schedule first update
        ui.delay(update_timer, 1)
    
    def check_timed_answer(self, sender):
        """Check answer in timed mode"""
        if not self.timer_running:
            return
            
        # Get the answer
        answer_field = sender.answer_field
        user_answer = answer_field.text.strip()
        
        # Calculate time taken
        time_taken = (datetime.now() - self.round_start_time).total_seconds()
        
        # Check answer
        result = self.game.check_answer(user_answer, time_taken)
        
        # Quick feedback (flash green/red)
        flash_view = ui.View(frame=(0, 0, 500, 500))
        flash_view.background_color = CORRECT_COLOR if result['correct'] else INCORRECT_COLOR
        flash_view.alpha = 0.3
        self.nav_view.present_view.add_subview(flash_view)
        
        def remove_flash():
            flash_view.remove_from_superview()
        
        ui.delay(remove_flash, 0.3)
        
        # Generate next question if timer still running
        if self.timer_running:
            # Generate new question
            question_data = self.game.generate_question()
            self.current_question = question_data[0]
            self.correct_answer = question_data[1]
            
            # Update the view
            question_label = self.nav_view.present_view.subviews[-5]  # Find the question label
            score_label = self.nav_view.present_view.subviews[-6]     # Find the score label
            
            # Update question and score
            question_label.text = f'Calculate: {self.current_question}'
            score_label.text = f'Score: {self.game.total_score} | Solved: {self.game.correct_count}'
            
            # Clear answer field
            answer_field.text = ''
            answer_field.begin_editing()
            
            # Reset start time
            self.round_start_time = datetime.now()
    
    def show_timed_summary(self):
        """Show summary after timed challenge"""
        summary_view = ui.View()
        summary_view.name = 'Challenge Complete'
        summary_view.background_color = BACKGROUND_COLOR
        
        # Title
        title_label = ui.Label(frame=(0, 30, 500, 40))
        title_label.text = 'Time\'s Up!'
        title_label.alignment = ui.ALIGN_CENTER
        title_label.font = ('Helvetica-Bold', 28)
        title_label.text_color = TINT_COLOR
        title_label.center = (summary_view.width * 0.5, 50)
        title_label.flex = 'WLRTB'
        summary_view.add_subview(title_label)
        
        # Get stats
        correct_count = self.game.correct_count
        wrong_count = self.game.wrong_count
        total_attempted = correct_count + wrong_count
        accuracy = (correct_count / total_attempted) * 100 if total_attempted > 0 else 0
        total_score = self.game.total_score
        
        # Stats container
        stats_view = ui.View(frame=(0, 90, 300, 160))
        stats_view.border_width = 1
        stats_view.border_color = LIGHT_GRAY
        stats_view.corner_radius = 10
        stats_view.center = (summary_view.width * 0.5, 170)
        stats_view.flex = 'LR'
        
        # Stats labels
        y_pos = 15
        font_size = 16
        line_height = 30
        
        stats_labels = [
            f"Questions Attempted: {total_attempted}",
            f"Correct Answers: {correct_count}",
            f"Accuracy: {accuracy:.1f}%",
            f"Questions Per Minute: {(total_attempted / (self.game.time_limit / 60)):.1f}",
            f"Total Score: {total_score} points"
        ]
        
        for text in stats_labels:
            label = ui.Label(frame=(20, y_pos, 260, line_height))
            label.text = text
            label.font = ('Helvetica', font_size)
            stats_view.add_subview(label)
            y_pos += line_height
        
        summary_view.add_subview(stats_view)
        
        # Action buttons
        y_offset = 280
        button_width = 200
        button_height = 50
        button_spacing = 20
        
        # Save score button
        save_btn = self.create_button('Save Score', 
                               frame=(0, y_offset, button_width, button_height),
                               action=self.save_timed_score)
        save_btn.center = (summary_view.width * 0.5, y_offset + button_height/2)
        save_btn.flex = 'LR'
        summary_view.add_subview(save_btn)
        
        # Main menu button
        y_offset += button_height + button_spacing
        menu_btn = self.create_button('Main Menu', 
                               frame=(0, y_offset, button_width, button_height),
                               action=self.return_to_main_menu)
        menu_btn.center = (summary_view.width * 0.5, y_offset + button_height/2)
        menu_btn.flex = 'LR'
        summary_view.add_subview(menu_btn)
        
        # Save stats for high score
        op_name = self.question_module.get_operation_name(self.game.operation_type)
        diff_name = "Medium"  # Timed mode uses medium difficulty
        
        # Prepare game stats
        self.game_stats = {
            'total_rounds': total_attempted,
            'correct_count': correct_count,
            'accuracy': accuracy,
            'avg_time': self.game.time_limit / total_attempted if total_attempted > 0 else 0,
            'total_score': total_score,
            'operation': op_name,
            'difficulty': diff_name,
            'timed_mode': True
        }
        
        self.nav_view.push_view(summary_view)
    
    def save_timed_score(self, sender):
        """Save timed challenge score"""
        self.save_high_score(sender)
    
    def show_about(self, sender):
        """Show about screen"""
        about_view = ui.View()
        about_view.name = 'About MathMaster'
        about_view.background_color = BACKGROUND_COLOR
        
        # Title
        title_label = ui.Label(frame=(0, 30, 500, 40))
        title_label.text = 'About MathMaster'
        title_label.alignment = ui.ALIGN_CENTER
        title_label.font = ('Helvetica-Bold', 24)
        title_label.center = (about_view.width * 0.5, 50)
        title_label.flex = 'WLRTB'
        about_view.add_subview(title_label)
        
        # App description
        desc = ui.TextView(frame=(20, 90, about_view.width - 40, 300))
        desc.text = """MathMaster is a math practice app designed to help improve mental math skills through regular practice.

Features:
• Multiple operation types: addition, subtraction, multiplication, division, fractions, percentages, exponents, and arrays
• Difficulty levels: Easy, Medium, Hard, and Adaptive
• Timed challenge mode
• Performance tracking with high scores
• Touch-friendly UI for Pythonista on iOS

Tips:
• Practice daily for best results
• Start with easier levels and work your way up
• Try to improve your speed without sacrificing accuracy
• Use the adaptive difficulty for personalized challenge

Version 1.0
© 2023
"""
        desc.font = ('Helvetica', 16)
        desc.editable = False
        desc.background_color = 'clear'
        about_view.add_subview(desc)
        
        # Back button
        back_btn = self.create_button('Back', 
                              frame=(0, 400, 200, 50),
                              action=self.return_to_main_menu)
        back_btn.center = (about_view.width * 0.5, 425)
        back_btn.flex = 'LR'
        about_view.add_subview(back_btn)
        
        self.nav_view.push_view(about_view)


def main():
    """Run the MathMaster UI app"""
    if not PYTHONISTA_AVAILABLE:
        print("This UI requires Pythonista on iOS. Please use the CLI version instead.")
        return
        
    # Clear the console
    console.clear()
    
    # Create and present the app
    math_app = MathGameUI()
    math_app.nav_view.present('fullscreen')


if __name__ == '__main__':
    main()
