import numpy as np
import pandas as pd


class LPSolver:
    def __init__(self):
        self.basic_vars = []
        self.var_names = []
        self.steps = []
        self.answer = None

    def create_simplex_tableau(self, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted):
        if ">=" in rel_coeffs or "=" in rel_coeffs:
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

    def solve_simplex(self, maximize, tableau_df):
        if tableau_df is None:
            print("Unsolvable with simplex")
            return None, self.steps, None

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

        # Detect infeasibility
        for i in range(tableau.shape[0] - 1):
            if tableau[i, -1] < 0 and np.all(tableau[i, :-1] <= 0):
                print("Infeasible solution detected.")
                return None, self.steps, None

        while np.any(tableau[-1, :-1] < 0 if maximize else tableau[-1, :-1] > 0):
            pivot_col = np.argmin(tableau[-1, :-1]) if maximize else np.argmax(tableau[-1, :-1])
            ratios = np.full(tableau.shape[0] - 1, np.inf)

            for i in range(tableau.shape[0] - 1):
                if tableau[i, pivot_col] > 0:
                    ratios[i] = tableau[i, -1] / tableau[i, pivot_col]

            valid_ratios = np.where(ratios > 0, ratios, np.inf)
            pivot_row = np.argmin(valid_ratios) if np.any(ratios > 0) else None

            # Detect unboundedness
            if pivot_row is None:
                print("Unbounded solution detected.")
                return None, self.steps, None

            self.basic_vars[pivot_row] = self.var_names[pivot_col]
            tableau[pivot_row] /= tableau[pivot_row, pivot_col]

            self.steps.append(pd.DataFrame(tableau.copy(), index=self.basic_vars + ["Z"], columns=self.var_names))

            for i in range(tableau.shape[0]):
                if i != pivot_row:
                    tableau[i] -= tableau[pivot_row] * tableau[i, pivot_col]

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
objective_coeffs = [30, -4]  # Objective function coefficients (for x1, x2)
constraint_coeffs = [[1, 0], [5, -1]]  # Constraint coefficients
rel_coefss = ["<=", "<="]
rhs_values = [5, 30]  # Target values
restricted = [True, False]

tableau = solver.create_simplex_tableau(objective_coeffs, constraint_coeffs, rhs_values, rel_coefss, restricted)
z, steps, answer = solver.solve_simplex(maximize=True, tableau_df=tableau)
for step in steps:
    print(step)
