import numpy as np
import pandas as pd
from simplexMethods.simplex import SimplexSolver


class LPSolver:
    def __init__(self):
        self.simplexSolver = SimplexSolver()

    def simplex(self, maximize, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted):
        tableau = self.simplexSolver._create_tableau(objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted)
        return self.simplexSolver._solve(maximize, tableau)

    def solve_bigm(self, objective_coeffs, constraint_coeffs, constraint_relations, rhs_values):
        # To be implemented
        pass

    def solve_two_phase(self, objective_coeffs, constraint_coeffs, constraint_relations, rhs_values):
        # To be implemented
        pass

    def _create_goal_tableau(self, objective_coeffs, constraint_coeffs, rhs_values):
        num_constraints = len(constraint_coeffs)
        num_variables = len(constraint_coeffs[0])

        # Each constraint has two deviation variables (d+ and d-)
        tableau = np.zeros((num_constraints + 1, num_variables + num_constraints * 2 + 1))

        # Fill the constraint coefficients
        tableau[:-1, :num_variables] = constraint_coeffs

        # Always include both d+ and d- for every constraint
        for i in range(num_constraints):
            tableau[i, num_variables + i * 2] = -1  # d+
            tableau[i, num_variables + i * 2 + 1] = 1  # d-

        # RHS values (targets)
        tableau[:-1, -1] = rhs_values

        # Objective function: Minimize sum of deviations (all d+ and d- variables)
        tableau[-1, num_variables:num_variables + num_constraints * 2] = 1

        return tableau

    def solve_goal_programming(self, objective_coeffs, constraint_coeffs, rel_coeffs, rhs_values):
        tableau = self._create_goal_tableau(objective_coeffs, constraint_coeffs, rhs_values)

        num_constraints = len(constraint_coeffs)
        num_variables = len(constraint_coeffs[0])

        # Variable names
        self.var_names = (
                [f"x{i + 1}" for i in range(num_variables)] +
                [item for i in range(num_constraints) for item in (f"d{i + 1}+", f"d{i + 1}-")] +
                ["RHS"]
        )

        self.basic_vars = [f"d{i + 1}-" for i in range(num_constraints)]  # Start with d- as basic vars
        self.steps.append(pd.DataFrame(tableau.copy(), index=self.basic_vars + ["Z"], columns=self.var_names))
        # TODO: create [z1,z2,...] with P

        return self.steps[-1]  # Return the final tableau as DataFrame


# solver = LPSolver()
# objective_coeffs = [2, 1]  # Objective function coefficients (for x1, x2)
# constraint_coeffs = [[1, 1], [1, -1]]  # Constraint coefficients
# rel_coefss = ["<=", "<="]
# rhs_values = [6, 4]  # Target values
# restricted = [True, True]
#
# tableau = solver.create_simplex_tableau(objective_coeffs, constraint_coeffs, rhs_values, rel_coefss, restricted)
# z, steps, answer = solver.solve_simplex(maximize=True, tableau_df=tableau)
# for step in steps:
#     print(step)

solver = LPSolver()
maximize = True
objective_coeffs = [30, -4]  # Objective function coefficients (for x1, x2)
constraint_coeffs = [[1, 0], [5, -1]]  # Constraint coefficients
rel_coeffs = ["<=", "<="]
rhs_values = [5, 30]  # Target values
restricted = [True, False]

z, steps, answer = solver.simplex(maximize, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted)
for step in steps:
    print(step)
