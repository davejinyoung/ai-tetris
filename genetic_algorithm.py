import random
import numpy as np
from agent import TetrisAgent
from Tetris import main as run_tetris_game

# --- Genetic Algorithm Parameters ---
POPULATION_SIZE = 50
NUM_GENERATIONS = 10
MUTATION_RATE = 0.25
MUTATION_STRENGTH = 0.1

class GeneticAlgorithm:
    def __init__(self):
        self.population = self.initialize_population()

    def initialize_population(self):
        """Creates an initial population of agents with random weights."""
        population = []
        for _ in range(POPULATION_SIZE):
            # Weights are initialized between 0 and 1
            # weights = np.array([0.37831685, 0.49987323, 0.51730053, 0.14835932])
            weights = np.random.rand(4)
            population.append(TetrisAgent(weights=weights))
        return population

    def run_generation(self, generation):
        """Runs a single generation of the genetic algorithm."""
        # Create seed for current generation so that all games have same sequence of pieces
        random.seed(generation)
        # 1. Evaluate Fitness
        fitness_scores = []
        for i, agent in enumerate(self.population):
            print(f"  - Running game for agent {i+1}/{POPULATION_SIZE}...")
            # The fitness is the score returned by the game
            score = run_tetris_game(is_training=True, agent=agent)
            fitness_scores.append(score)
            print(f"    Agent {i+1} finished with score: {score}")

        # 2. Selection
        # Combine agents and their scores, then sort by score
        population_with_scores = sorted(zip(self.population, fitness_scores), key=lambda x: x[1], reverse=True)
        
        # Select the top 20% of the population as parents
        num_parents = POPULATION_SIZE // 5
        parents = [agent for agent, score in population_with_scores[:num_parents]]

        # 3. Crossover and Mutation
        next_generation = []
        
        # Keep the best agent from the current generation (elitism)
        if parents:
            next_generation.append(parents[0])

        # Create the rest of the new population
        while len(next_generation) < POPULATION_SIZE:
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            
            # Create child's weights
            child_weights = self.crossover(parent1.weights, parent2.weights)
            
            # Mutate the child's weights
            mutated_child_weights = self.mutate(child_weights)
            
            # Create a new agent with the new weights
            next_generation.append(TetrisAgent(weights=mutated_child_weights))
            
        self.population = next_generation

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
                # Add a random value to the weight
                mutation = np.random.uniform(-MUTATION_STRENGTH, MUTATION_STRENGTH)
                mutated_weights[i] += mutation
        return mutated_weights

def train():
    """Main function to run the training process."""
    ga = GeneticAlgorithm()
    
    for generation in range(NUM_GENERATIONS):
        print(f"--- Starting Generation {generation+1}/{NUM_GENERATIONS} ---")
        ga.run_generation(generation)
        
        # Optionally, save the best weights of this generation
        best_agent = ga.population[0]
        print(f"--- Generation {generation+1} Complete. Best Weights: {best_agent.weights} ---")
        np.save('best_weights.npy', best_agent.weights)

if __name__ == '__main__':
    train()
