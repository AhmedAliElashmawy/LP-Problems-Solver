import numpy as np
import pandas as pd


class LPSolver:
    def __init__(self):
        self.basic_vars = []
        self.var_names = []
        self.steps = []
        self.answer = ()

    def _create_simplex_tableau(self, objective_coeffs, constraint_coeffs, rhs_values):
        self.basic_vars = []
        self.var_names = []
        self.steps = []

        num_constraints, num_variables = len(constraint_coeffs), len(objective_coeffs)
        tableau = np.zeros((num_constraints + 1, num_variables + num_constraints + 1))

        # Fill the tableau
        tableau[:-1, :num_variables] = constraint_coeffs
        np.fill_diagonal(tableau[:-1, num_variables:num_variables + num_constraints], 1)  # Slack variables
        tableau[:-1, -1] = rhs_values  # RHS values

        # For minimization, negate the objective function coefficients
        tableau[-1, :num_variables] = -1 * np.array(objective_coeffs)

        return tableau

    def solve_simplex(self, maximize, objective_coeffs, constraint_coeffs, rel_coeffs, rhs_values):
        for relation in rel_coeffs:
            if relation != "<=":
                print("Simplex is not appropriate!")
                return None, None, None
        tableau = self._create_simplex_tableau(objective_coeffs, constraint_coeffs, rhs_values)

        num_constraints, num_variables = len(constraint_coeffs), len(objective_coeffs)
        self.var_names = [f"x{i + 1}" for i in range(num_variables)] + [f"s{i + 1}" for i in
                                                                        range(num_constraints)] + [
                             "RHS"]
        self.basic_vars = [f"s{i + 1}" for i in range(num_constraints)]  # Slack variables as initial basis
        self.steps.append(pd.DataFrame(tableau.copy(), index=self.basic_vars + ["Z"], columns=self.var_names))

        while np.any(tableau[-1, :-1] < 0 if maximize else tableau[-1, :-1] > 0):  # Different condition for min/max
            pivot_col = np.argmin(tableau[-1, :-1]) if maximize else np.argmax(
                tableau[-1, :-1])  # Different pivot selection
            ratios = np.full(tableau.shape[0] - 1, np.inf)

            # Compute ratios for minimum positive ratio test
            for i in range(tableau.shape[0] - 1):
                if tableau[i, pivot_col] > 0:
                    ratios[i] = tableau[i, -1] / tableau[i, pivot_col]

            pivot_row = np.argmin(ratios) if np.any(ratios < np.inf) else None  # Row with min ratio

            if pivot_row is None:
                print("No feasible solution found.")
                return None

            # Update basic variables
            self.basic_vars[pivot_row] = self.var_names[pivot_col]

            # Pivoting: Normalize the pivot row
            tableau[pivot_row] /= tableau[pivot_row, pivot_col]

            # Store step after pivot row normalization
            self.steps.append(pd.DataFrame(tableau.copy(), index=self.basic_vars + ["Z"], columns=self.var_names))

            # Update all rows (except pivot row)
            for i in range(tableau.shape[0]):
                if i != pivot_row:
                    tableau[i] -= tableau[pivot_row] * tableau[i, pivot_col]

            # Store step after full pivot update
            self.steps.append(pd.DataFrame(tableau.copy(), index=self.basic_vars + ["Z"], columns=self.var_names))
            new_rhs = dict(zip(self.basic_vars, tableau[:-1, -1]))
            self.answer = tuple(new_rhs.get(var, 0) for var in self.var_names if var.startswith("x"))

        return tableau[-1, -1] * (1 if maximize else -1), self.steps, self.answer

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
            tableau[i, num_variables + i * 2] = -1   # d+
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
        #TODO: create [z1,z2,...] with P

        return self.steps[-1]  # Return the final tableau as DataFrame





solver = LPSolver()
objective_coeffs = [1, 2]  # Objective function coefficients (for x1, x2)
constraint_coeffs = [[1, 1], [2, 3]]  # Constraint coefficients
rhs_values = [10, 20]  # Target values

final_tableau = solver.solve_goal_programming(objective_coeffs, constraint_coeffs, ["<=", "="], rhs_values)
print(final_tableau)
