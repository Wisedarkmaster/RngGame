import tkinter as tk
import random
import threading
import time
import os
import json

LEADERBOARD_FILE = r"c:\Users\admin\Desktop\rng_leaderboard.txt"
PROFILES_FILE = r"c:\Users\admin\Desktop\rng_profiles.txt"

THEMES = {
    "Dark Blue": {"bg": "#222244", "fg": "#00FFCC", "btn": "#00CC66", "btn_fg": "white"},
    "Light": {"bg": "#F0F0F0", "fg": "#007777", "btn": "#FFD700", "btn_fg": "#222244"},
    "Classic": {"bg": "#FFFFFF", "fg": "#000000", "btn": "#AAAAAA", "btn_fg": "#000000"},
    "Pink": {"bg": "#FFB6C1", "fg": "#8B008B", "btn": "#FF69B4", "btn_fg": "#FFFFFF"},
}

class RNGGame:
    def __init__(self, master):
        self.master = master
        self.theme = "Dark Blue"
        self.apply_theme()
        master.title("RNG Game")

        self.range_min = 1
        self.range_max = 10
        self.lucky_number = random.randint(self.range_min, self.range_max)
        self.attempts = 0
        self.animating = False

        self.stats = {"games": 0, "total_attempts": 0, "wins": 0}
        self.high_score = None
        self.leaderboard = []
        self.achievements = set()
        self.win_streak = 0

        self.profile_var = tk.StringVar()
        self.profiles = {}
        self.current_profile = None

        self.profile_menu = None

        self.history = []
        self.unlocked_mascots = {"neutral"}
        self.selected_mascot = "neutral"
        self.mascot_menu = None
        self.mascot_menu_var = tk.StringVar(value=self.selected_mascot)

        # --- Create all widgets before load_profiles ---
        self.menu_frame = tk.Frame(master, bg=self.bg)
        self.menu_label = tk.Label(self.menu_frame, text="Welcome to RNG Game!", font=("Arial", 20, "bold"), bg=self.bg, fg=self.fg)
        self.menu_label.pack(pady=20)
        self.profile_label = tk.Label(self.menu_frame, text="Profile:", font=("Arial", 12), bg=self.bg, fg=self.fg)
        self.profile_label.pack()

        self.game_frame = tk.Frame(master, bg=self.bg)
        self.range_frame = tk.Frame(self.game_frame, bg=self.bg)
        self.range_frame.pack(pady=5)
        tk.Label(self.range_frame, text="Min:", bg=self.bg, fg=self.fg).pack(side=tk.LEFT)
        self.min_entry = tk.Entry(self.range_frame, width=4)
        self.min_entry.insert(0, str(self.range_min))
        self.min_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(self.range_frame, text="Max:", bg=self.bg, fg=self.fg).pack(side=tk.LEFT)
        self.max_entry = tk.Entry(self.range_frame, width=4)
        self.max_entry.insert(0, str(self.range_max))
        self.max_entry.pack(side=tk.LEFT, padx=2)
        self.set_range_button = tk.Button(self.range_frame, text="Set Range", command=self.set_range)
        self.set_range_button.pack(side=tk.LEFT, padx=5)

        self.lucky_frame = tk.Frame(self.game_frame, bg=self.bg)
        self.lucky_frame.pack(pady=5)
        tk.Label(self.lucky_frame, text="Lucky Number:", bg=self.bg, fg=self.fg).pack(side=tk.LEFT)
        self.lucky_entry = tk.Entry(self.lucky_frame, width=6)
        self.lucky_entry.pack(side=tk.LEFT, padx=2)
        self.set_lucky_button = tk.Button(self.lucky_frame, text="Set Lucky Number", command=self.set_lucky_number)
        self.set_lucky_button.pack(side=tk.LEFT, padx=5)

        self.mascot_canvas = tk.Canvas(self.game_frame, width=80, height=80, bg=self.bg, highlightthickness=0)
        self.mascot_canvas.pack(pady=5)
        self.mascot_state = "neutral"
        self.draw_mascot(self.selected_mascot)

        self.mascot_menu = tk.OptionMenu(self.game_frame, self.mascot_menu_var, *self.unlocked_mascots, command=self.change_mascot)
        self.mascot_menu.pack(pady=2)

        self.theme_var = tk.StringVar(value=self.theme)
        self.theme_menu = tk.OptionMenu(self.game_frame, self.theme_var, *THEMES.keys(), command=self.change_theme)
        self.theme_menu.config(bg=self.btn, fg=self.btn_fg, font=("Arial", 10))
        self.theme_menu["menu"].config(bg=self.bg, fg=self.fg)
        self.theme_menu.pack(pady=2)

        self.range_label = tk.Label(self.game_frame, text=f"Current Range: {self.range_min} - {self.range_max}", 
                                    bg=self.bg, fg="#FFD700", font=("Arial", 12, "bold"))
        self.range_label.pack(pady=5)

        self.label = tk.Label(self.game_frame, text="Try to roll the lucky number!", 
                              bg=self.bg, fg=self.fg, font=("Arial", 16, "bold"))
        self.label.pack(pady=10)

        self.result_label = tk.Label(self.game_frame, text="", bg=self.bg, fg=self.fg, font=("Arial", 14))
        self.result_label.pack(pady=5)

        self.roll_button = tk.Button(self.game_frame, text="Roll", command=self.roll, font=("Arial", 14, "bold"), bg=self.btn, fg=self.btn_fg)
        self.roll_button.pack(pady=10, ipadx=10, ipady=5)

        self.reset_button = tk.Button(self.game_frame, text="Reset Game", command=self.reset_game, font=("Arial", 12), bg="#4444AA", fg="white")
        self.reset_button.pack(pady=5, ipadx=5, ipady=2)

        self.stats_label = tk.Label(self.game_frame, text=self.get_stats_text(), bg=self.bg, fg="#FFA500", font=("Arial", 11, "bold"), justify=tk.LEFT)
        self.stats_label.pack(pady=5)

        self.high_score_label = tk.Label(self.game_frame, text=self.get_high_score_text(), bg=self.bg, fg="#00FF00", font=("Arial", 11, "bold"))
        self.high_score_label.pack(pady=2)

        self.leaderboard_label = tk.Label(self.game_frame, text=self.get_leaderboard_text(), bg=self.bg, fg="#00BFFF", font=("Arial", 10), justify=tk.LEFT)
        self.leaderboard_label.pack(pady=5)

        self.achievements_label = tk.Label(self.game_frame, text=self.get_achievements_text(), bg=self.bg, fg="#FF69B4", font=("Arial", 10, "bold"), justify=tk.LEFT)
        self.achievements_label.pack(pady=5)

        self.history_label = tk.Label(self.game_frame, text=self.get_history_text(), bg=self.bg, fg="#888888", font=("Arial", 9), justify=tk.LEFT)
        self.history_label.pack(pady=5)

        self.confetti_canvas = tk.Canvas(self.game_frame, width=350, height=100, bg=self.bg, highlightthickness=0)
        self.confetti_canvas.pack(pady=0)
        # --- End widgets before load_profiles ---

        self.settings_frame = tk.Frame(master, bg=self.bg)
        self.settings_label = tk.Label(self.settings_frame, text="Settings", font=("Arial", 18, "bold"), bg=self.bg, fg=self.fg)
        self.settings_label.pack(pady=10)
        self.theme_settings_var = tk.StringVar(value=self.theme)
        self.theme_settings_menu = tk.OptionMenu(self.settings_frame, self.theme_settings_var, *THEMES.keys())
        self.theme_settings_menu.pack(pady=5)
        self.save_settings_btn = tk.Button(self.settings_frame, text="Save Settings", command=self.save_settings)
        self.save_settings_btn.pack(pady=5)
        self.back_settings_btn = tk.Button(self.settings_frame, text="Back", command=self.show_menu)
        self.back_settings_btn.pack(pady=5)

        self.load_profiles()
        self.create_profile_menu()
        self.profile_menu.pack()
        self.new_profile_entry = tk.Entry(self.menu_frame)
        self.new_profile_entry.pack()
        self.add_profile_btn = tk.Button(self.menu_frame, text="Add Profile", command=self.add_profile)
        self.add_profile_btn.pack(pady=2)
        self.start_button = tk.Button(self.menu_frame, text="Start Game", font=("Arial", 14, "bold"), bg=self.btn, fg=self.btn_fg, command=self.show_game)
        self.start_button.pack(pady=10, ipadx=10, ipady=5)
        self.settings_button = tk.Button(self.menu_frame, text="Settings", font=("Arial", 12), command=self.show_settings)
        self.settings_button.pack(pady=2)
        self.menu_frame.pack(fill="both", expand=True)

    def create_profile_menu(self):
        if self.profile_menu:
            self.profile_menu.destroy()
        profile_names = list(self.profiles.keys())
        if not profile_names:
            profile_names = ["Default"]
        self.profile_menu = tk.OptionMenu(
            self.menu_frame,
            self.profile_var,
            profile_names[0],
            *profile_names[1:],
            command=self.select_profile
        )
        self.profile_var.set(self.current_profile)

    def load_profiles(self):
        try:
            with open(PROFILES_FILE, "r") as f:
                self.profiles = json.load(f)
        except Exception:
            self.profiles = {"Default": {}}
        if not self.profiles:
            self.profiles = {"Default": {}}
        self.current_profile = list(self.profiles.keys())[0]
        self.profile_var.set(self.current_profile)
        self.load_current_profile_data()

    def add_profile(self):
        name = self.new_profile_entry.get().strip()
        if name and name not in self.profiles:
            if self.current_profile:
                self.save_current_profile_data()
            self.profiles[name] = {}
            self.save_profiles()
            self.current_profile = name
            self.profile_var.set(name)
            self.create_profile_menu()
            self.load_current_profile_data()

    def select_profile(self, name):
        if self.current_profile:
            self.save_current_profile_data()
        self.current_profile = name
        self.load_current_profile_data()
        profile = self.profiles.get(name, {})
        self.theme = profile.get("theme", "Dark Blue")
        self.theme_settings_var.set(self.theme)
        self.apply_theme()

    def save_current_profile_data(self):
        if self.current_profile:
            self.profiles[self.current_profile]["stats"] = self.stats
            self.profiles[self.current_profile]["high_score"] = self.high_score
            self.profiles[self.current_profile]["leaderboard"] = self.leaderboard
            self.profiles[self.current_profile]["achievements"] = list(self.achievements)
            self.profiles[self.current_profile]["history"] = self.history
            self.profiles[self.current_profile]["unlocked_mascots"] = list(self.unlocked_mascots)
            self.profiles[self.current_profile]["selected_mascot"] = self.selected_mascot
            self.save_profiles()

    def load_current_profile_data(self):
        profile = self.profiles.get(self.current_profile, {})
        self.stats = profile.get("stats", {"games": 0, "total_attempts": 0, "wins": 0})
        self.high_score = profile.get("high_score", None)
        self.leaderboard = profile.get("leaderboard", [])
        self.achievements = set(profile.get("achievements", []))
        self.history = profile.get("history", [])
        self.unlocked_mascots = set(profile.get("unlocked_mascots", ["neutral"]))
        self.selected_mascot = profile.get("selected_mascot", "neutral")
        self.update_mascot_menu()
        self.mascot_menu_var.set(self.selected_mascot)
        self.draw_mascot(self.selected_mascot)
        self.history_label.config(text=self.get_history_text())

    def save_profiles(self):
        try:
            with open(PROFILES_FILE, "w") as f:
                json.dump(self.profiles, f)
        except Exception:
            pass

    def save_settings(self):
        self.theme = self.theme_settings_var.get()
        if self.current_profile:
            self.profiles[self.current_profile]["theme"] = self.theme
            self.save_profiles()
        self.apply_theme()
        self.show_menu()

    def show_game(self):
        self.menu_frame.pack_forget()
        self.settings_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)

    def show_menu(self):
        self.settings_frame.pack_forget()
        self.game_frame.pack_forget()
        self.menu_frame.pack(fill="both", expand=True)

    def show_settings(self):
        self.menu_frame.pack_forget()
        self.settings_frame.pack(fill="both", expand=True)

    def apply_theme(self):
        theme = THEMES[self.theme]
        self.bg = theme["bg"]
        self.fg = theme["fg"]
        self.btn = theme["btn"]
        self.btn_fg = theme["btn_fg"]
        if hasattr(self, "master"):
            self.master.configure(bg=self.bg)

    def change_theme(self, value):
        self.theme = value
        self.apply_theme()
        self.master.configure(bg=self.bg)
        self.range_frame.configure(bg=self.bg)
        self.lucky_frame.configure(bg=self.bg)
        self.mascot_canvas.configure(bg=self.bg)
        self.game_frame.configure(bg=self.bg)
        self.menu_frame.configure(bg=self.bg)
        self.menu_label.configure(bg=self.bg, fg=self.fg)
        self.profile_label.configure(bg=self.bg, fg=self.fg)
        self.start_button.configure(bg=self.btn, fg=self.btn_fg)
        self.settings_button.configure(bg=self.btn, fg=self.btn_fg)
        for widget in self.range_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=self.bg, fg=self.fg)
        for widget in self.lucky_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=self.bg, fg=self.fg)
        self.theme_menu.config(bg=self.btn, fg=self.btn_fg)
        self.theme_menu["menu"].config(bg=self.bg, fg=self.fg)
        self.range_label.configure(bg=self.bg)
        self.label.configure(bg=self.bg, fg=self.fg)
        self.result_label.configure(bg=self.bg, fg=self.fg)
        self.roll_button.configure(bg=self.btn, fg=self.btn_fg)
        self.stats_label.configure(bg=self.bg)
        self.high_score_label.configure(bg=self.bg)
        self.leaderboard_label.configure(bg=self.bg)
        self.achievements_label.configure(bg=self.bg)
        self.confetti_canvas.configure(bg=self.bg)
        self.settings_frame.configure(bg=self.bg)
        self.settings_label.configure(bg=self.bg, fg=self.fg)
        self.theme_settings_menu.configure(bg=self.btn, fg=self.btn_fg)
        self.save_settings_btn.configure(bg=self.btn, fg=self.btn_fg)
        self.back_settings_btn.configure(bg=self.btn, fg=self.btn_fg)
        self.history_label.configure(bg=self.bg, fg="#888888")

    def set_lucky_number(self):
        try:
            lucky = int(self.lucky_entry.get())
            if not (self.range_min <= lucky <= self.range_max):
                self.result_label.config(text=f"Lucky number must be between {self.range_min} and {self.range_max}.", fg="orange")
                return
            self.lucky_number = lucky
            self.result_label.config(text=f"Lucky number set to {lucky}.", fg="#00FFCC")
        except ValueError:
            self.result_label.config(text="Please enter a valid number.", fg="orange")

    def set_range(self):
        try:
            min_val = int(self.min_entry.get())
            max_val = int(self.max_entry.get())
            if min_val >= max_val:
                self.result_label.config(text="Min must be less than Max.", fg="orange")
                return
            self.range_min = min_val
            self.range_max = max_val
            self.range_label.config(text=f"Current Range: {self.range_min} - {self.range_max}")
            if not (self.range_min <= self.lucky_number <= self.range_max):
                self.lucky_number = random.randint(self.range_min, self.range_max)
                self.lucky_entry.delete(0, tk.END)
            self.reset_game()
        except ValueError:
            self.result_label.config(text="Please enter valid numbers.", fg="orange")

    def draw_mascot(self, state):
        self.mascot_canvas.delete("all")
        if state == "cool":
            self.mascot_canvas.create_oval(10, 10, 70, 70, fill="#AEEEEE", outline="#888")
            self.mascot_canvas.create_rectangle(25, 35, 55, 45, fill="black")
            self.mascot_canvas.create_line(20, 40, 25, 40, fill="black", width=3)
            self.mascot_canvas.create_line(55, 40, 60, 40, fill="black", width=3)
            self.mascot_canvas.create_line(30, 60, 50, 60, fill="#000", width=3)
        else:
            face_color = "#FFFFFF"
            mouth = (30, 60, 50, 60, 40, 65)
            self.mascot_canvas.create_oval(10, 10, 70, 70, fill=face_color, outline="#888")
            self.mascot_canvas.create_oval(25, 30, 35, 40, fill="#000")
            self.mascot_canvas.create_oval(45, 30, 55, 40, fill="#000")
            self.mascot_canvas.create_line(*mouth, smooth=True, width=3, fill="#000")

    def update_mascot_menu(self):
        if self.mascot_menu is None:
            return
        menu = self.mascot_menu["menu"]
        menu.delete(0, "end")
        for mascot in self.unlocked_mascots:
            menu.add_command(label=mascot, command=lambda m=mascot: self.change_mascot(m))

    def change_mascot(self, mascot):
        self.selected_mascot = mascot
        self.mascot_menu_var.set(mascot)
        self.draw_mascot(mascot)
        self.save_current_profile_data()

    def animate_mascot_bounce(self):
        for _ in range(6):
            self.mascot_canvas.move("all", 0, -5)
            self.mascot_canvas.update()
            time.sleep(0.05)
            self.mascot_canvas.move("all", 0, 5)
            self.mascot_canvas.update()
            time.sleep(0.05)

    def roll(self):
        if self.animating:
            return
        self.animating = True
        self.roll_button.config(state=tk.DISABLED)
        threading.Thread(target=self.animate_roll).start()

    def animate_roll(self):
        cycles = 15
        for i in range(cycles):
            fake_roll = random.randint(self.range_min, self.range_max)
            self.result_label.config(
                text=f"You rolled: {fake_roll}\nRolling...",
                fg="#AAAAFF"
            )
            self.draw_mascot(self.selected_mascot)
            time.sleep(0.07 + i * 0.01)

        self.attempts += 1
        roll = random.randint(self.range_min, self.range_max)
        if roll == self.lucky_number:
            self.result_label.config(
                text=f"You rolled: {roll}\nCongratulations! You hit the lucky number in {self.attempts} attempts!",
                fg="#00FF00"
            )
            self.roll_button.config(state=tk.DISABLED)
            self.stats["games"] += 1
            self.stats["wins"] += 1
            self.stats["total_attempts"] += self.attempts
            self.win_streak += 1
            self.update_high_score(self.attempts)
            self.update_leaderboard(self.attempts)
            self.save_stats()
            self.check_achievements()
            self.achievements_label.config(text=self.get_achievements_text())
            self.show_confetti()
            self.draw_mascot(self.selected_mascot)
            self.animate_mascot_bounce()
            self.history.append(f"Win: {roll} in {self.attempts} attempts")
            if self.stats["wins"] >= 10:
                self.unlocked_mascots.add("cool")
                self.update_mascot_menu()
        else:
            self.result_label.config(
                text=f"You rolled: {roll}\nNot the lucky number. Try again!",
                fg="#FF5555"
            )
            self.roll_button.config(state=tk.NORMAL)
            self.win_streak = 0
            self.draw_mascot(self.selected_mascot)
            self.animate_mascot_bounce()
            self.history.append(f"Miss: {roll}")
        self.history = self.history[-10:]
        self.history_label.config(text=self.get_history_text())
        self.stats_label.config(text=self.get_stats_text())
        self.high_score_label.config(text=self.get_high_score_text())
        self.leaderboard_label.config(text=self.get_leaderboard_text())
        self.save_current_profile_data()
        self.animating = False

    def reset_game(self):
        if not self.lucky_entry.get():
            self.lucky_number = random.randint(self.range_min, self.range_max)
        if self.attempts > 0 and self.result_label.cget("fg") != "#00FF00":
            self.stats["games"] += 1
            self.stats["total_attempts"] += self.attempts
            self.save_stats()
            self.save_current_profile_data()
        self.attempts = 0
        self.result_label.config(text="", fg=self.fg)
        self.roll_button.config(state=tk.NORMAL)
        self.stats_label.config(text=self.get_stats_text())
        self.high_score_label.config(text=self.get_high_score_text())
        self.leaderboard_label.config(text=self.get_leaderboard_text())
        self.achievements_label.config(text=self.get_achievements_text())
        self.win_streak = 0
        self.confetti_canvas.delete("all")
        self.history.clear()
        self.history_label.config(text=self.get_history_text())
        self.draw_mascot(self.selected_mascot)

    def get_history_text(self):
        if not self.history:
            return "History: No rolls yet."
        return "History:\n" + "\n".join(self.history)

    def update_high_score(self, attempts):
        if self.high_score is None or attempts < self.high_score:
            self.high_score = attempts

    def update_leaderboard(self, attempts):
        self.leaderboard.append(attempts)
        self.leaderboard = sorted(self.leaderboard)[:5]
        self.save_stats()

    def get_high_score_text(self):
        return f"High Score (fewest attempts): {self.high_score if self.high_score is not None else 'N/A'}"

    def get_leaderboard_text(self):
        if not self.leaderboard:
            return "Leaderboard: No scores yet."
        text = "Leaderboard (Top 5):\n"
        for idx, score in enumerate(self.leaderboard, 1):
            text += f"{idx}. {score} attempts\n"
        return text.strip()

    def get_stats_text(self):
        games = self.stats["games"]
        wins = self.stats["wins"]
        total_attempts = self.stats["total_attempts"]
        avg = (total_attempts / games) if games else 0
        win_rate = (wins / games * 100) if games else 0
        return (f"Games Played: {games}\n"
                f"Wins: {wins}\n"
                f"Average Attempts: {avg:.2f}\n"
                f"Win Rate: {win_rate:.1f}%")

    def check_achievements(self):
        if self.attempts == 1:
            self.achievements.add("Lucky Shot: Win in 1 attempt!")
        if self.stats["games"] >= 10:
            self.achievements.add("Veteran: Played 10 games!")
        if self.win_streak >= 5:
            self.achievements.add("Hot Streak: 5 wins in a row!")
        if self.high_score is not None and self.high_score <= 2:
            self.achievements.add("Master RNG: High score of 2 or less!")
        if self.stats["wins"] >= 20:
            self.achievements.add("Champion: 20 total wins!")
        if self.stats["wins"] >= 10:
            self.achievements.add("Cool Cat: 10 wins unlocks cool mascot!")
            self.unlocked_mascots.add("cool")
            self.update_mascot_menu()

    def get_achievements_text(self):
        if not self.achievements:
            return "Achievements: None yet."
        text = "Achievements Unlocked:\n"
        for ach in sorted(self.achievements):
            text += f"• {ach}\n"
        return text.strip()

    def show_confetti(self):
        import random as pyrandom
        self.confetti_canvas.delete("all")
        confetti = []
        colors = ["#FF69B4", "#FFD700", "#00FFCC", "#00BFFF", "#FF5555", "#00FF00", "#FFA500"]
        for _ in range(30):
            x = pyrandom.randint(10, 340)
            y = pyrandom.randint(10, 90)
            color = pyrandom.choice(colors)
            oval = self.confetti_canvas.create_oval(x, y, x+8, y+8, fill=color, outline="")
            confetti.append(oval)

        def animate_confetti(step=0):
            if step > 15:
                self.confetti_canvas.delete("all")
                return
            for oval in confetti:
                dx = pyrandom.randint(-2, 2)
                dy = pyrandom.randint(2, 5)
                self.confetti_canvas.move(oval, dx, dy)
            self.confetti_canvas.after(50, lambda: animate_confetti(step+1))

        animate_confetti()

    def load_stats(self):
        if not os.path.exists(LEADERBOARD_FILE):
            return
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                lines = f.readlines()
                if lines:
                    self.stats = eval(lines[0].strip())
                if len(lines) > 1:
                    self.high_score = int(lines[1].strip())
                if len(lines) > 2:
                    self.leaderboard = [int(x) for x in lines[2].strip().split(",") if x]
        except Exception:
            pass

    def save_stats(self):
        try:
            with open(LEADERBOARD_FILE, "w") as f:
                f.write(str(self.stats) + "\n")
                f.write(str(self.high_score if self.high_score is not None else "") + "\n")
                f.write(",".join(str(x) for x in self.leaderboard))
        except Exception:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    game = RNGGame(root)
    root.mainloop()