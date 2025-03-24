import numpy as np
import pandas as pd
from .LpInterface import LPSolverInterface


class SimplexSolver(LPSolverInterface):
    def __init__(self):
        self.basic_vars = []
        self.var_names = []
        self.steps = []
        self.answer = None

    def create_tableau(self, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted):
        if "≥" in rel_coeffs or "=" in rel_coeffs:
            print("Simplex isn't the right method!")
            return None

        num_constraints, num_variables = len(constraint_coeffs), len(objective_coeffs)

        unrestricted_variables = sum(1 for val in restricted if not val)
        total_variables = num_variables + unrestricted_variables  # Extra columns for unrestricted variables

        tableau = np.zeros((num_constraints + 1, total_variables + num_constraints + 1))

        var_index = 0
        expanded_constraint_coeffs = []
        expanded_objective_coeffs = []
        var_names = []

        for i in range(num_variables):
            if restricted[i]:
                expanded_constraint_coeffs.append([row[i] for row in constraint_coeffs])
                expanded_objective_coeffs.append(objective_coeffs[i])
                var_names.append(f"x{i + 1}")
            else:
                expanded_constraint_coeffs.append([row[i] for row in constraint_coeffs])
                expanded_constraint_coeffs.append([-row[i] for row in constraint_coeffs])
                # expanded are already in LHS but objective still in RHS
                expanded_objective_coeffs.append(objective_coeffs[i])
                expanded_objective_coeffs.append(-objective_coeffs[i])
                var_names.append(f"x{i + 1}+")
                var_names.append(f"x{i + 1}-")

        tableau[:-1, :len(expanded_constraint_coeffs)] = np.array(expanded_constraint_coeffs).T
        np.fill_diagonal(
            tableau[:-1, len(expanded_constraint_coeffs):len(expanded_constraint_coeffs) + num_constraints],
            1)  # Slack vars
        tableau[:-1, -1] = rhs_values
        tableau[-1, :len(expanded_objective_coeffs)] = -1 * np.array(expanded_objective_coeffs)  # Min objective

        var_names += [f"s{i + 1}" for i in range(num_constraints)] + ["RHS"]
        self.var_names = var_names
        self.basic_vars = [f"s{i + 1}" for i in range(num_constraints)]

        return pd.DataFrame(tableau, index=self.basic_vars + ["Z"], columns=self.var_names)

    def solve(self, maximize, tableau_df):
        if tableau_df is None:
            return "Unsolvable with simplex", self.steps

        tableau = tableau_df.to_numpy()
        self.var_names = list(tableau_df.columns)
        self.basic_vars = list(tableau_df.index[:-1])
        self.steps.append(tableau_df.copy())

        for i, bv in enumerate(self.basic_vars):
            col_index = self.var_names.index(bv)
            if tableau[-1][col_index] != 0:
                factor = tableau[-1][col_index] / tableau[i][col_index]
                tableau[-1] -= factor * tableau[i]
                self.steps.append(pd.DataFrame(tableau.copy(), index=self.basic_vars + ["Z"], columns=self.var_names))


        while np.any(tableau[-1, :-1] < 0 if maximize else tableau[-1, :-1] > 0):
            pivot_col = np.argmin(tableau[-1, :-1]) if maximize else np.argmax(tableau[-1, :-1])
            ratios = np.full(tableau.shape[0] - 1, np.inf)

            for i in range(tableau.shape[0] - 1):
                if tableau[i, pivot_col] > 0:
                    ratios[i] = tableau[i, -1] / tableau[i, pivot_col]

            valid_ratios = np.where(ratios > 0, ratios, np.inf)
            pivot_row = np.argmin(valid_ratios) if np.any(ratios > 0) else None

            # Detect unbounded
            if pivot_row is None:
                return "Unbounded solution detected.", self.steps

            self.basic_vars[pivot_row] = self.var_names[pivot_col]
            tableau[pivot_row] /= tableau[pivot_row, pivot_col]

            self.steps.append(pd.DataFrame(tableau.copy(), index=self.basic_vars + ["Z"], columns=self.var_names))

            for i in range(tableau.shape[0]):
                if i != pivot_row:
                    tableau[i] -= tableau[pivot_row] * tableau[i, pivot_col]

            self.steps.append(pd.DataFrame(tableau.copy(), index=self.basic_vars + ["Z"], columns=self.var_names))

            new_rhs = dict(zip(self.basic_vars, tableau[:-1, -1]))

            self.answer = tuple(new_rhs.get(var, 0) for var in self.var_names if var.startswith("x"))

        for var, value in new_rhs.items():
            if var.startswith("a") and abs(value) > 1e-7:
                for step in self.steps:
                    print(step)
                return "Infeasible solution detected.", self.steps

        return None, self.steps

