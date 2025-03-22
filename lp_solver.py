import numpy as np
import pandas as pd
from simplexMethods.simplex import SimplexSolver
from simplexMethods.goalProgrammingValues import GoalProgrammingValueSolver
from simplexMethods.goalProgrammingPriority import GoalProgrammingPrioritySolver
from simplexMethods.bigM import BigMSolver
from simplexMethods.TwoPhase import TwoPhaseSolver

class LPSolver:
    def __init__(self):
        self.simplex_solver = SimplexSolver()
        self.big_M = BigMSolver()
        self.two_phase = TwoPhaseSolver()
        self.goal_programming_value_solver = GoalProgrammingValueSolver()
        self.goal_programming_priority_solver = GoalProgrammingPrioritySolver()

    def simplex(self, maximize, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted):
        tableau = self.simplex_solver.create_tableau(objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted)
        error, steps = self.simplex_solver.solve(maximize, tableau)
        return error, steps

    def big_M(self, maximize, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted):
        tableu = self.big_M.create_tableau(objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted)
        error, steps = self.big_M.solve(maximize , tableu)
        return error , steps

    def two_phase(self, maximize, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted):
        tableu = self.two_phase.create_tableau(objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted)
        error, steps = self.two_phase.solve(maximize , tableu)
        return error , steps


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

#       x1  x2+  x2-    s1   s2    RHS
# x1   1.0  0.0  0.0   1.0  0.0    5.0
# x2-  0.0 -1.0  1.0  -5.0  1.0    5.0
# Z    0.0  0.0  0.0  10.0  4.0  170.0

# ========== PRIORITY-BASED SOLVER USAGE ==========
priority_solver = LPSolver()
objective_coeffs = None
constraint_coeffs = [
    [7, 3],
    [10, 5],
    [5, 4],
    [100, 60]
]
rhs_values = [40, 60, 35, 600]
rel_coeffs = ["≥", "≥", "≥", "≤"]
goals = [1, 2, 3, 4]

error, steps = priority_solver.goal_programming_with_priority_levels(False, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, goals)
print("\nPriority-Based Goal Programming Error:", error)
for step in steps:
    print(step)

#      x1 x2      d1+      d1-    d2+ d2-    d3+ d3-        d4+         d4-      RHS
# x1   1  0     -1/2      1/2      0   0      0   0       1/40       -1/40        5
# d2-  0  0      5/6     -5/6     -1   1      0   0       1/24       -1/24      5/3
# d3-  0  0     -5/6      5/6      0   0     -1   1     13/120     -13/120     10/3
# x2   0  1      5/6     -5/6      0   0      0   0     -7/120       7/120      5/3
# Z1   0  0      -P1      -P1      0   0      0   0          0           0        0
# Z2   0  0   5*P2/6  -5*P2/6  -2*P2   0      0   0      P2/24      -P2/24   5*P2/3
# Z3   0  0  -5*P3/6   5*P3/6      0   0  -2*P3   0  13*P3/120  -13*P3/120  10*P3/3
# Z4   0  0        0        0      0   0      0   0        -P4         -P4        0

