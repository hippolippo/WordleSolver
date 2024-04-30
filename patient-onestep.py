from WordleBenchmark.solver_interface import WordleSolver
from WordleBenchmark.wordle import Wordle
import json
import time

FIRST_WORD = "roate"
HARDMODE = False

try:
    cache = json.load(open(f"{FIRST_WORD}-cache.json"))
except FileNotFoundError:
    print(f"No cache found for first word {FIRST_WORD}")
    print(f"This will result is slower solutions")
    cache = None


class PatientOnestep(WordleSolver):

    def __init__(self):
        with open("old_potential_answers") as file:
            self.possible_words = file.read().splitlines()
        with open("valid_words") as file:
            self.valid_words = file.read().splitlines()

    def pick_word(self):
        best_size = None
        best_word = None
        c = 0
        for word in (self.possible_words if HARDMODE else self.valid_words):
            c += 1
            groups = dict()
            for next_guess in self.possible_words:
                score = Wordle.Score(word, next_guess)
                if score.hash not in groups:
                    groups[score.hash] = 1
                else:
                    groups[score.hash] += 1
            expected_size = sum([g**2 for g in groups.values()])
            if word in self.possible_words: expected_size -= 1
            if best_size is None or expected_size < best_size:
                best_size = expected_size
                best_word = word
        return best_word
    
    def get_guess(self, score: Wordle.Score) -> str:
        self.possible_words = list(filter(lambda word: Wordle.Score(score.word, word) == score, self.possible_words))
        if cache is not None and not HARDMODE:
            if score.word == FIRST_WORD:
                return cache[str(score.hash)]
        return self.pick_word()
    
    def get_first_guess(self) -> str:
        return FIRST_WORD

def benchmark():    
    from WordleBenchmark.benchmark import benchmark, print_summary
    import json
    results = benchmark(PatientOnestep)
    print_summary(results)
    with open("results", "w") as file:
        json.dump(results, file)


def play(word):
    solver = PatientOnestep()
    c = 0
    guess = solver.get_first_guess()
    print(Wordle.Score(guess, word))
    while ((c:=c+1) < 20) and (guess := solver.get_guess(Wordle.Score(guess, word))) != word:
        print(Wordle.Score(guess, word))
    print(Wordle.Score(guess, word))
    print(solver.possible_words)
    
def generate_cache(first_guess):
    words = PatientOnestep().possible_words
    thing = dict()
    out = dict()
    for word in words:
        score = Wordle.Score(first_guess, word)
        if score.hash not in thing:
            thing[score.hash] = score
    for a in thing:
        s = PatientOnestep()
        out[a] = s.get_guess(thing[a])
        print(thing[a], out[a])
    with open(f"{first_guess}-cache.json","w") as file:
        json.dump(out, file)

if __name__ == "__main__":
    instance = PatientOnestep()
    running = True
    while running:
        print(f"""
    Welcome to Wordle Solver!
    Select an option:
    1. Set Starting Guess ({FIRST_WORD})
    2. Toggle Hardmode ({HARDMODE})
    3. Generate Cache for starting word
    4. Solve for known word
    5. Run Benchmark
    6. Quit
            """)
        option = input("Select an option: ")
        if option not in {"1", "2", "3", "4", "5", "6"}:
            print("Invalid Option\n")
            continue
        if option == "1":
            temp = input("Enter a new starting word: ")
            if temp not in instance.valid_words:
                print(f"{temp} is not a valid wordle guess\n")
                continue
            FIRST_WORD = temp
            print(f"Starting guess set to {FIRST_WORD}\n")
            try:
                cache = json.load(open(f"{FIRST_WORD}-cache.json"))
            except FileNotFoundError:
                print(f"No cache found for first word {FIRST_WORD}")
                print(f"This will result is slower solutions")
                cache = None
        if option == "2":
            HARDMODE = not HARDMODE
            print(f"Set hardmode to {HARDMODE}\n")
        if option == "3":
            temp = input("Input the starting word: ")
            if temp not in instance.valid_words:
                print(f"{temp} is not a valid wordle guess\n")
                continue
            generate_cache(temp)
            print(f"Cache Generated for {temp}")
            if temp == FIRST_WORD:
                cache = json.load(open(f"{FIRST_WORD}-cache.json"))
                print(f"Cache now loaded for starting word {FIRST_WORD}")
        if option == "4":
            temp = input("Input the goal word: ")
            if temp not in PatientOnestep().possible_words:
                print(f"{temp} is not a valid wordle answer\n")
                continue
            play(temp)
        if option == "5":
            benchmark()
        if option == "6":
            print("Goodbye!")
            running = False
        time.sleep(1)
        