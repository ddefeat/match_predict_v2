# Betting Strategy Optimization

This project implements an ELO-based betting strategy for predicting sports outcomes and a Genetic Algorithm to optimize the strategy parameters. The project consists of two main components:
1. `create_elo.py`: Calculates and simulates betting outcomes using an ELO-based prediction system.
2. `genetic_algorithm.py`: Uses a Genetic Algorithm to optimize the parameters in `create_elo.py` for maximizing betting balance and minimizing variance in performance across multiple seasons.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Files](#files)
- [Installation](#installation)
- [Usage](#usage)
  - [Running the ELO Model](#running-the-elo-model)
  - [Optimizing with the Genetic Algorithm](#optimizing-with-the-genetic-algorithm)
- [Configuration](#configuration)
- [Results](#results)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project provides a framework for betting strategy based on an ELO rating system, which adjusts teams' ratings based on their game results. The ratings are used to predict the expected outcome of future games. The strategy is further optimized by a Genetic Algorithm (GA), which tunes key parameters to maximize average balance and minimize balance variance across seasons.

## Features

- **ELO-based Betting Strategy**: Uses a customized ELO rating to estimate probabilities of match outcomes and calculates betting returns based on these predictions.
- **Parameter Optimization with GA**: Optimizes parameters, including `Factor`, `K`, `Floor`, `Win Rate Floor`, and `Ceil`, to improve the performance of the betting strategy.
- **Stability Emphasis**: The GA also minimizes the variance in betting results across seasons, aiming for stable performance.

## Files

### `create_elo.py`
The core betting strategy file. This script:
- Implements an ELO-based method to evaluate betting on games using team performance.
- Predicts returns based on ELO-adjusted ratings and game odds.
- Simulates betting over a set of historical games to track balance.

### `genetic_algorithm.py`
The optimization module. This script:
- Runs a GA to tune parameters in `create_elo.py`.
- Considers both average balance and stability (standard deviation of balance) across seasons for the fitness function.
- Outputs the best set of parameters after optimization.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/betting-strategy-optimization.git