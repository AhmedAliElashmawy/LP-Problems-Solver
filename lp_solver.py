import numpy as np
import pandas as pd
from simplexMethods.simplex import SimplexSolver
from simplexMethods.goalProgrammingValues import GoalProgrammingSolver



class LPSolver:
    def __init__(self):
        self.simplex_solver = SimplexSolver()
        self.goal_programming_solver = GoalProgrammingSolver()


    def simplex(self, maximize, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted):
        tableau = self.simplex_solver.create_tableau(objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted)
        return self.simplex_solver.solve(maximize, tableau)

    def solve_bigm(self, objective_coeffs, constraint_coeffs, constraint_relations, rhs_values):
        # To be implemented
        pass

    def solve_two_phase(self, objective_coeffs, constraint_coeffs, constraint_relations, rhs_values):
        # To be implemented
        pass

    def goal_programming_with_priority_values(self, maximize, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, goals):
        tableau = self.goal_programming_solver.create_tableau(objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, goals)
        return self.goal_programming_solver.solve(maximize, tableau)

    def goal_programming_with_priority_levels(self, maximize, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, goals):
        tableau = self.goal_programming_solver.create_tableau(objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, goals)
        return self.goal_programming_solver.solve(maximize, tableau)


# solver = LPSolver()
# maximize = True
# objective_coeffs = [30, -4]  # Objective function coefficients (for x1, x2)
# constraint_coeffs = [[1, 0], [5, -1]]  # Constraint coefficients
# rel_coeffs = ["<=", "<="]
# rhs_values = [5, 30]  # Target values
# restricted = [True, False]
#
# z, steps, answer = solver.simplex(maximize, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted)
# for step in steps:
#     print(step)


# Example usage
# solver = LPSolver()
# objective_coeffs = [4, 8]  # Coefficients for x1 and x2
# constraint_coeffs = [
#     [4, 8],  # x1 + 2x2 ≤ 8
#     [8, 24],  # 3x1 + x2 ≤ 12
#     [1, 2],  # 3x1 + x2 ≤ 12
#     [1, 0]  # 3x1 + x2 ≤ 12
#
# ]
# rhs_values = [45, 100, 10, 6]  # Right-hand side values
# rel_coeffs = [">=", "<=", "<=", "<="]  # Relation signs
# goals = [2, 1, 0, 0]  # Goals for deviation
# maximize = True
#
# z, steps, answer = solver.goal_programming(maximize, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, goals)
# for step in steps:
#     print(step)

# Example usage
solver = LPSolver()
objective_coeffs = None  # Coefficients for x1 and x2
constraint_coeffs = [
    [2, 3],  # x1 + 2x2 ≤ 8
    [1, 0],  # 3x1 + x2 ≤ 12
    [0, 1],  # 3x1 + x2 ≤ 12
]
rhs_values = [640, 200, 120]  # Right-hand side values
rel_coeffs = ["<=", ">=", ">="]  # Relation signs
goals = [0, 1, 1]  # Goals for deviation
maximize = True

z, steps, answer = solver.goal_programming_with_priority_values(maximize, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, goals)
for step in steps:
    print(step)
