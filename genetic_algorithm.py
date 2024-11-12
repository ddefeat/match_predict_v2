import random
import numpy as np
from create_elo import main

# Define ranges for the parameters
FACTOR_RANGE = (100, 800)
K_RANGE = (10, 50)
FLOOR_RANGE = (0.3, 0.6)
WIN_RATE_FLOOR_RANGE = (0.1, 0.5)
CEIL_RANGE = (0.9, 1.5)
SEASONS = ["22-23", "23-24"]

# Genetic Algorithm Parameters
POPULATION_SIZE = 20
GENERATIONS = 10
MUTATION_RATE = 0.1
TOURNAMENT_SIZE = 5

# Define weights for the fitness function
BALANCE_WEIGHT = 1.0
STABILITY_WEIGHT = 0.25

def random_individual():
    """Generate a random individual with parameters excluding season."""
    return {
        "factor": random.uniform(*FACTOR_RANGE),
        "k": random.randint(*K_RANGE),
        "floor": random.uniform(*FLOOR_RANGE),
        "win_rate_floor": random.uniform(*WIN_RATE_FLOOR_RANGE),
        "ceil": random.uniform(*CEIL_RANGE)
    }

def evaluate_individual(individual):
    """Evaluate an individual by averaging fitness across all seasons and minimizing balance variance."""
    # Calculate balances for each season
    balances = [main(
        factor=individual["factor"],
        k=individual["k"],
        floor=individual["floor"],
        win_rate_floor=individual["win_rate_floor"],
        ceil=individual["ceil"],
        season=season
    ) for season in SEASONS]
    
    # Calculate mean and standard deviation of balances
    avg_balance = np.mean(balances)
    balance_std = np.std(balances)  # Use np.var(balances) if variance is preferred
    
    # Combine average balance and stability (negative standard deviation) in fitness
    fitness = (BALANCE_WEIGHT * avg_balance) - (STABILITY_WEIGHT * balance_std)
    return fitness

def tournament_selection(population, fitnesses):
    selected = random.sample(list(zip(population, fitnesses)), TOURNAMENT_SIZE)
    return max(selected, key=lambda x: x[1])[0]

def crossover(parent1, parent2):
    child1, child2 = {}, {}
    for key in parent1:
        if random.random() < 0.5:
            child1[key], child2[key] = parent1[key], parent2[key]
        else:
            child1[key], child2[key] = parent2[key], parent1[key]
    return child1, child2

def mutate(individual):
    if random.random() < MUTATION_RATE:
        individual["factor"] = random.uniform(*FACTOR_RANGE)
    if random.random() < MUTATION_RATE:
        individual["k"] = random.randint(*K_RANGE)
    if random.random() < MUTATION_RATE:
        individual["floor"] = random.uniform(*FLOOR_RANGE)
    if random.random() < MUTATION_RATE:
        individual["win_rate_floor"] = random.uniform(*WIN_RATE_FLOOR_RANGE)
    if random.random() < MUTATION_RATE:
        individual["ceil"] = random.uniform(*CEIL_RANGE)

def genetic_algorithm():
    population = [random_individual() for _ in range(POPULATION_SIZE)]
    for generation in range(GENERATIONS):
        fitnesses = [evaluate_individual(ind) for ind in population]
        new_population = []
        while len(new_population) < POPULATION_SIZE:
            parent1 = tournament_selection(population, fitnesses)
            parent2 = tournament_selection(population, fitnesses)
            child1, child2 = crossover(parent1, parent2)
            mutate(child1)
            mutate(child2)
            new_population.extend([child1, child2])
        population = new_population
    final_fitnesses = [evaluate_individual(ind) for ind in population]
    best = population[final_fitnesses.index(max(final_fitnesses))]
    return best, max(final_fitnesses)

# Run GA
best_solution, best_fitness = genetic_algorithm()
print("Best solution:", best_solution)
print("Best fitness (average balance adjusted for stability):", best_fitness)