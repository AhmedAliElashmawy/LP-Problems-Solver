import numpy as np
import pandas as pd
from simplexMethods.simplex import SimplexSolver
from simplexMethods.goalProgrammingValues import GoalProgrammingValueSolver
from simplexMethods.goalProgrammingPriority import GoalProgrammingPrioritySolver


class LPSolver:
    def __init__(self):
        self.simplex_solver = SimplexSolver()
        self.goal_programming_value_solver = GoalProgrammingValueSolver()
        self.goal_programming_priority_solver = GoalProgrammingPrioritySolver()

    def simplex(self, maximize, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted):
        tableau = self.simplex_solver.create_tableau(objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted)
        error, steps = self.simplex_solver.solve(maximize, tableau)
        return error, steps

    def goal_programming_with_priority_values(self, maximize, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, goals):
        tableau = self.goal_programming_value_solver.create_tableau(objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, goals)
        error, steps = self.goal_programming_value_solver.solve(maximize, tableau)
        return error, steps

    def goal_programming_with_priority_levels(self, maximize, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, goals):
        tableau = self.goal_programming_priority_solver.create_tableau(objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, goals)
        error, steps = self.goal_programming_priority_solver.solve(maximize, tableau)
        return error, steps


# # ========== SIMPLEX SOLVER ==========
# solver = LPSolver()
# maximize = True
# objective_coeffs = [30, -4]
# constraint_coeffs = [[1, 0], [5, -1]]
# rel_coeffs = ["<=", "<="]
# rhs_values = [5, 30]
# restricted = [True, False]
#
# error, steps = solver.simplex(maximize, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted)
# print("\nSimplex Method Error:", error)
# for step in steps:
#     print(step)

# # ========== PRIORITY-BASED SOLVER USAGE ==========
# priority_solver = LPSolver()
# objective_coeffs = None
# constraint_coeffs = [
#     [7, 3],
#     [10, 5],
#     [5, 4],
#     [100, 60]
# ]
# rhs_values = [40, 60, 35, 600]
# rel_coeffs = [">=", ">=", ">=", "<="]
# goals = [1, 2, 3, 4]
#
# error, steps = priority_solver.goal_programming_with_priority_levels(False, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, goals)
# print("\nPriority-Based Goal Programming Error:", error)
# for step in steps:
#     print(step)

