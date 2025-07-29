import random
import numpy as np
import matplotlib.pyplot as plt
import re
from agent import TetrisAgent
from Tetris import main as run_tetris_game

# --- Genetic Algorithm Parameters ---
POPULATION_SIZE = 50
NUM_GENERATIONS = 50
MUTATION_RATE = 0.1
MUTATION_STRENGTH = 0.1


class GeneticAlgorithm:
    def __init__(self):
        self.population = self.initialize_population()

    def initialize_population(self):
        """Creates an initial population of agents with random weights."""
        population = []
        for _ in range(POPULATION_SIZE):
            # Weights are initialized between 0 and 1f
            # weights = np.array([0.37831685, 0.49987323, 0.51730053, 0.14835932])
            weights = np.random.rand(4)
            population.append(TetrisAgent(weights=weights))
        return population

    def run_generation(self, generation):
        """
        Runs a single generation of the genetic algorithm.
        Returns key scores and metrics for the generation.
        """
        # 1. Evaluate Fitness
        fitness_scores = []
        for i, agent in enumerate(self.population):
            print(f"  - Running game for agent {i + 1}/{POPULATION_SIZE}...")
            # The fitness is the score returned by the game
            score = run_tetris_game(is_training=True, agent=agent)
            fitness_scores.append(score)
            print(f"    Agent {i + 1} finished with score: {score}")

        # --- Calculate and store metrics for plotting ---
        best_score = np.max(fitness_scores)
        avg_score = np.mean(fitness_scores)
        worst_score = np.min(fitness_scores)

        # Calculate the standard deviation of weights for each parameter to measure diversity
        all_weights = np.array([agent.weights for agent in self.population])
        weight_std_dev = np.std(all_weights, axis=0)

        # 2. Selection
        population_with_scores = sorted(zip(self.population, fitness_scores), key=lambda x: x[1], reverse=True)

        num_parents = POPULATION_SIZE // 5
        parents = [agent for agent, score in population_with_scores[:num_parents]]

        # 3. Crossover and Mutation
        next_generation = []

        # Elitism: Keep the best agent from the current generation
        if parents:
            best_agent_this_gen = population_with_scores[0][0]
            next_generation.append(best_agent_this_gen)

        # Create the rest of the new population
        while len(next_generation) < POPULATION_SIZE:
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)

            child_weights = self.crossover(parent1.weights, parent2.weights)
            mutated_child_weights = self.mutate(child_weights)
            next_generation.append(TetrisAgent(weights=mutated_child_weights))

        self.population = next_generation

        # Return all relevant metrics for this generation
        return best_score, avg_score, worst_score, best_agent_this_gen.weights, weight_std_dev

    def crossover(self, weights1, weights2):
        """Performs single-point crossover between two parent weight vectors."""
        crossover_point = random.randint(1, len(weights1) - 1)
        child_weights = np.concatenate([weights1[:crossover_point], weights2[crossover_point:]])
        return child_weights

    def mutate(self, weights):
        """Applies mutation to a weight vector."""
        mutated_weights = np.copy(weights)
        for i in range(len(mutated_weights)):
            if random.random() < MUTATION_RATE:
                mutation = np.random.uniform(-MUTATION_STRENGTH, MUTATION_STRENGTH)
                mutated_weights[i] += mutation
        return mutated_weights


# def plot_learning_curve(history):
#     """Plots the learning curve showing the best, average, and worst scores."""
#     best_scores = [h['best_score'] for h in history]
#     avg_scores = [h['avg_score'] for h in history]
#     worst_scores = [h['worst_score'] for h in history]
#     generations = range(1, len(history) + 1)
#
#     plt.figure(figsize=(12, 7))
#     plt.plot(generations, best_scores, marker='o', linestyle='-', color='g', label='Best Score')
#     plt.plot(generations, avg_scores, marker='o', linestyle='--', color='b', label='Average Score')
#     plt.plot(generations, worst_scores, marker='o', linestyle=':', color='r', label='Worst Score')
#
#     plt.title('Tetris AI Learning Curve', fontsize=16)
#     plt.xlabel('Generation', fontsize=12)
#     plt.ylabel('Fitness Score', fontsize=12)
#     plt.xticks(generations)
#     plt.grid(True)
#     plt.legend()
#     plt.show()


# def plot_weight_evolution(history):
#     """Plots how the weights of the best agent evolve over generations."""
#     best_weights_history = np.array([h['best_weights'] for h in history])
#     generations = range(1, len(history) + 1)
#
#     plt.figure(figsize=(12, 7))
#     for i in range(best_weights_history.shape[1]):
#         plt.plot(generations, best_weights_history[:, i], marker='o', linestyle='-', label=f'Weight {i + 1}')
#
#     plt.title('Best Agent: Weight Evolution Over Generations', fontsize=16)
#     plt.xlabel('Generation', fontsize=12)
#     plt.ylabel('Weight Value', fontsize=12)
#     plt.xticks(generations)
#     plt.grid(True)
#     plt.legend()
#     plt.show()


def plot_genetic_diversity(history):
    """Plots the standard deviation of weights in the population over generations."""
    diversity_history = np.array([h['diversity'] for h in history])
    generations = range(1, len(history) + 1)

    plt.figure(figsize=(12, 7))
    for i in range(diversity_history.shape[1]):
        plt.plot(generations, diversity_history[:, i], marker='o', linestyle='-', label=f'Weight {i + 1} Std Dev')

    plt.title('Genetic Diversity of Population', fontsize=16)
    plt.xlabel('Generation', fontsize=12)
    plt.ylabel('Standard Deviation of Weights', fontsize=12)
    plt.xticks(generations)
    plt.grid(True)
    plt.legend()
    plt.show()


def parse_weights_from_file(filepath='generation_weights.txt'):
    """
    Parses the generation_weights.txt file to extract the weight vectors.
    """
    history = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                # Use regex to find the list-like string (e.g., "[0.73, ...]")
                match = re.search(r'\[(.*?)\]', line)
                if match:
                    # Extract the content inside the brackets, split by comma, and convert to float
                    weights_str = match.group(1).split(',')
                    weights = [float(w.strip()) for w in weights_str]
                    history.append({'best_weights': np.array(weights)})
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        print("Please make sure the script is in the same directory as your weights file.")
        return None
    return history


def train():
    """Main function to run the training process."""
    ga = GeneticAlgorithm()
    history = []

    for generation in range(NUM_GENERATIONS):
        print(f"--- Starting Generation {generation + 1}/{NUM_GENERATIONS} ---")
        best_score, avg_score, worst_score, best_weights, diversity = ga.run_generation(generation)

        history.append({
            'best_score': best_score,
            'avg_score': avg_score,
            'worst_score': worst_score,
            'best_weights': best_weights,
            'diversity': diversity
        })

        best_agent = ga.population[0]
        print(f"--- Generation {generation + 1} Complete ---")
        print(f"    Best Score: {best_score}")
        print(f"    Avg Score:  {avg_score:.2f}")
        print(f"    Best Weights: {best_agent.weights}")
        np.save('best_weights.npy', best_agent.weights)

    print("\n--- Training Complete. Generating visualizations... ---")
    plot_learning_curve(history)
    plot_weight_evolution(history)
    plot_genetic_diversity(history)


WEIGHTS_HISTORY = [
    {'generation': 5, 'best_weights': np.array([0.46259859, 0.54138918, 0.29247212, 0.19617962])},
    {'generation': 10, 'best_weights': np.array([0.44183742, 0.72305659, 0.35156238, 0.20983592])},
    {'generation': 15, 'best_weights': np.array([0.82231857, 0.57086229, 0.33633321, 0.20983592])},
    {'generation': 20, 'best_weights': np.array([0.74048663, 0.47834702, 0.33890547, 0.19813253])},
    {'generation': 25, 'best_weights': np.array([0.53072737, 0.72305659, 0.27176956, 0.19813253])},
    {'generation': 30, 'best_weights': np.array([0.55580476, 0.72305659, 0.31187495, 0.19813253])},
    {'generation': 35, 'best_weights': np.array([0.48572385, 0.7486866, 0.27176956, 0.19813253])},
    {'generation': 40, 'best_weights': np.array([0.53072737, 0.83967109, 0.32826192, 0.26066793])},
    {'generation': 45, 'best_weights': np.array([0.56585345, 0.83967109, 0.36161974, 0.26066793])},
    {'generation': 50, 'best_weights': np.array([0.52906766, 0.80255314, 0.32826192, 0.26066793])}
]


def plot_learning_curve(evaluation_history):
    """Generates a plot showing the best, average, and worst scores over generations."""
    generations = [d['generation'] for d in evaluation_history]
    best_scores = [d['best_score'] for d in evaluation_history]
    avg_scores = [d['avg_score'] for d in evaluation_history]
    worst_scores = [d['worst_score'] for d in evaluation_history]

    plt.figure(figsize=(12, 7))
    plt.plot(generations, best_scores, 'o-', label='Best Score', color='green', linewidth=2)
    plt.plot(generations, avg_scores, 's-', label='Average Score', color='blue', linewidth=2)
    plt.plot(generations, worst_scores, 'x-', label='Worst Score', color='red', linewidth=1, linestyle='--')

    plt.title('Agent Performance Over Generations', fontsize=16)
    plt.xlabel('Generation', fontsize=12)
    plt.ylabel('Score', fontsize=12)
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.xticks(generations)
    plt.tight_layout()
    plt.savefig('learning_curve.png')
    print("Saved learning_curve.png")
    plt.show()


def plot_weight_evolution(evaluation_history):
    """Generates a plot showing how each of the four weights evolved."""
    generations = [d['generation'] for d in evaluation_history]
    weights = np.array([d['best_weights'] for d in evaluation_history])

    labels = ['Lines Cleared', 'Holes', 'Aggregate Height', 'Bumpiness']

    plt.figure(figsize=(12, 7))
    for i in range(weights.shape[1]):
        plt.plot(generations, weights[:, i], 'o-', label=f'Weight {i + 1} ({labels[i]})')

    plt.title('Evolution of Heuristic Weights Over Generations', fontsize=16)
    plt.xlabel('Generation', fontsize=12)
    plt.ylabel('Weight Value', fontsize=12)
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.xticks(generations)
    plt.tight_layout()
    plt.savefig('weight_evolution.png')
    print("Saved weight_evolution.png")
    plt.show()


def evaluate():
    """Function to evaluate the hardcoded weights and generate plots."""
    evaluation_history = []

    # Iterate over the hardcoded weights history
    for gen_data in WEIGHTS_HISTORY:
        generation = gen_data['generation']
        current_weights = gen_data['best_weights']
        print(f'Evaluating Generation {generation} best weights: {current_weights}')

        fitness_scores = []
        # Run the agent 10 times with different seeds to get a stable performance measure
        for seed in range(150,161):
            random.seed(seed*2)  # Use a different seed for each run to test robustness
            agent = TetrisAgent(weights=current_weights)
            # Run the game in training mode (no visuals, max speed)
            score = run_tetris_game(agent=agent, is_training=True)
            fitness_scores.append(score)
            print(f"    Gen {generation}, Run {seed + 1}/10 -> Score: {score}")

        # Calculate metrics from the 10 runs
        best_score = np.max(fitness_scores)
        avg_score = np.mean(fitness_scores)
        worst_score = np.min(fitness_scores)

        evaluation_history.append({
            'generation': generation,
            'best_score': best_score,
            'avg_score': avg_score,
            'worst_score': worst_score,
            'best_weights': current_weights
        })

    print("\n--- Evaluation Complete. Generating visualizations... ---")
    plot_learning_curve(evaluation_history)
    plot_weight_evolution(evaluation_history)


if __name__ == '__main__':
    print(parse_weights_from_file()[0]['best_weights'])
    # train()
    evaluate()
