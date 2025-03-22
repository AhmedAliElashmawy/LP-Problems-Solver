import pandas as pd
import sympy as sp
from .LpInterface import LPSolverInterface
import sys





LARGE_NUMBER = sys.float_info.max


class GoalProgrammingPrioritySolver(LPSolverInterface):
    def __init__(self):
        self.basic_vars = []
        self.var_names = []
        self.steps = []
        self.answer = None

    def create_tableau(self, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, goals):

        if constraint_coeffs:
            num_constraints, num_variables = len(constraint_coeffs), len(constraint_coeffs[0])
        else:
            num_constraints, num_variables = 0, 0

        num_slack_vars = sum(1 for goal in goals if goal == 0)
        num_deviation_vars = sum(2 if goal != 0 else 0 for goal in goals)
        total_variables = num_variables + num_slack_vars + num_deviation_vars

        goals_vars = sum(1 for goal in goals if goal != 0)
        unique_sorted = sorted(set(goals) - {0})
        priority_map = {val: i + 1 for i, val in enumerate(unique_sorted)}
        priority_map[0] = 0
        rhs_values += [0] * goals_vars

        # Use SymPy matrix for symbolic computation
        tableau = sp.Matrix.zeros(num_constraints + goals_vars, total_variables + 1)

        var_names = []
        expanded_constraint_coeffs = [[0] * total_variables for _ in range(num_constraints)]
        deviation_vars = []
        slack_vars = []

        # Process normal variables (x1, x2, ...)
        for i in range(num_variables):
            var_names.append(f"x{i + 1}")
            for j in range(num_constraints):
                expanded_constraint_coeffs[j][i] = constraint_coeffs[j][i]

        # Process slack and deviation variables
        slack_index = num_variables
        deviation_index = num_variables + num_slack_vars
        deviation_indices = []

        for i in range(num_constraints):
            if goals[i] == 0:
                slack_var = f"S{i + 1}"
                slack_vars.append(slack_var)
                var_names.append(slack_var)

                expanded_constraint_coeffs[i][slack_index] = 1
                slack_index += 1

        for i in range(num_constraints):
            if goals[i] != 0:
                deviation_vars.append(f"d{i + 1}+")
                deviation_vars.append(f"d{i + 1}-")
                var_names.extend([f"d{i + 1}+", f"d{i + 1}-"])

                expanded_constraint_coeffs[i][deviation_index] = -1  # d+
                expanded_constraint_coeffs[i][deviation_index + 1] = 1  # d-
                deviation_indices.append([i, deviation_index])
                deviation_index += 2

        # Convert expanded_constraint_coeffs to SymPy Matrix
        expanded_constraint_coeffs = sp.Matrix(expanded_constraint_coeffs)

        # Fill the tableau with constraint coefficients (assign values element-wise)
        for i in range(num_constraints):
            for j in range(expanded_constraint_coeffs.shape[1]):
                tableau[i, j] = expanded_constraint_coeffs[i, j]

        # Process priority-based objective function
        deviation_index = num_variables + num_slack_vars
        for i in range(len(goals)):
            for j in range(len(deviation_indices)):
                if goals[i] != 0 and i == deviation_indices[j][0]:
                    if rel_coeffs[i] == "≤":
                        tableau[num_constraints + priority_map[goals[i]] - 1, deviation_indices[j][1]] = -sp.Symbol(f"P{goals[i]}")
                    elif rel_coeffs[i] == "≥":
                        tableau[num_constraints + priority_map[goals[i]] - 1, deviation_indices[j][1] + 1] = -sp.Symbol(f"P{goals[i]}")
                    else:
                        tableau[num_constraints + priority_map[goals[i]] - 1, deviation_indices[j][1]] = -sp.Symbol(f"P{goals[i]}")
                        tableau[num_constraints + priority_map[goals[i]] - 1, deviation_indices[j][1] + 1] = -sp.Symbol(f"P{goals[i]}")


        # Add RHS values
        for i in range(len(rhs_values)):
            tableau[i, -1] = rhs_values[i]

        var_names.append("RHS")
        self.var_names = var_names

        self.basic_vars = [
            f"d{i + 1}-" if f"d{i + 1}-" in deviation_vars else f"S{i + 1}" for i in range(num_constraints)
        ]

        return pd.DataFrame(
            tableau.tolist(),
            index=self.basic_vars + [f"Z{i+1}" for i in range(goals_vars)],
            columns=self.var_names
        )

    def solve(self, maximize, tableau_df):
        if tableau_df is None:
            return "Couldn't form tableau", self.steps

        tableau = sp.Matrix(tableau_df.values)
        self.var_names = list(tableau_df.columns)
        self.basic_vars = []
        goals_number = 0

        # Identify basic variables and goal rows
        for index in tableau_df.index:
            if str(index).startswith("Z"):
                goals_number += 1
                continue
            self.basic_vars.append(index)

        basic_variables_number = len(self.basic_vars)
        self.steps.append(tableau_df.copy())

        # Precompute priority values (Higher priority → Larger weight)
        priority_values = {
            f"P{i + 1}": 10 ** (goals_number * 10 - i) for i in range(goals_number)
        }

        for i, bv in enumerate(self.basic_vars):
            col_index = self.var_names.index(bv)
            for j in range(goals_number):
                if tableau[j + basic_variables_number, col_index] != 0:
                    factor = tableau[j + basic_variables_number, col_index] / tableau[i, col_index]
                    tableau[j + basic_variables_number, :] = tableau.row(
                        j + basic_variables_number) - factor * tableau.row(i)

        self.steps.append(pd.DataFrame(
            tableau.tolist(),
            index=self.basic_vars + [f"Z{i + 1}" for i in range(goals_number)],
            columns=self.var_names
        ))

        for j in range(goals_number):  # Iterate over each goal function Zj

            while True:
                numeric_tableau = tableau.subs(priority_values)
                # Select pivot column
                pivot_col = max(
                    range(numeric_tableau.shape[1] - 1),
                    key=lambda c: numeric_tableau[j + basic_variables_number, c].evalf()
                )

                # If no positive value left in row, move to next goal
                if all(x.evalf() <= 0 for x in numeric_tableau[j + basic_variables_number, :-1]):
                    break

                # Find pivot row using min-ratio test
                ratios = [LARGE_NUMBER] * basic_variables_number
                for i in range(basic_variables_number):
                    denominator = numeric_tableau[i, pivot_col]
                    numerator = numeric_tableau[i, -1]

                    if denominator > 0 and numerator >= 0:
                        ratios[i] = numerator / denominator

                # Find the row with the smallest ratio, avoiding invalid values
                valid_rows = [r for r in range(len(ratios)) if ratios[r] != 1e10]

                pivot_row = min(valid_rows, key=lambda r: ratios[r])

                if pivot_row is None:
                    return "No valid pivot row found. The problem may be unbounded.", self.steps

                # If the pivot row affects a previously optimized Zk, skip
                if any(numeric_tableau[k + basic_variables_number, pivot_col] < 0 for k in range(j)):
                    break  # Skip this step

                # Perform pivoting
                self.basic_vars[pivot_row] = self.var_names[pivot_col]
                tableau[pivot_row, :] = tableau.row(pivot_row) / tableau[pivot_row, pivot_col]
                numeric_tableau[pivot_row, :] = numeric_tableau.row(pivot_row) / numeric_tableau[pivot_row, pivot_col]

                for i in range(tableau.rows):
                    if i != pivot_row:
                        factor = tableau[i, pivot_col]
                        tableau[i, :] = tableau.row(i) - factor * tableau.row(pivot_row)

                        factor = numeric_tableau[i, pivot_col]
                        numeric_tableau[i, :] = numeric_tableau.row(i) - factor * numeric_tableau.row(pivot_row)

                # Save step
                self.steps.append(pd.DataFrame(
                    tableau.tolist(),
                    index=self.basic_vars + [f"Z{i + 1}" for i in range(goals_number)],
                    columns=self.var_names
                ))

        return None, self.steps


# solver = GoalProgrammingPrioritySolver()
# objective_coeffs = None
# constraint_coeffs = [
#     [7, 3],
#     [10, 5],
#     [5, 4],
#     [100, 60]
# ]
# rhs_values = [40, 60, 35, 600]
# rel_coeffs = [">=", ">=", ">=", "<="]
# goals = [1, 2, 3, 0]
# maximize = True
#
# tableau = solver.create_tableau(objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, goals)
# error, steps = solver.solve(False, tableau_df=tableau)
# for step in steps:
#     print(step)

# solver = GoalProgrammingPrioritySolver()
# objective_coeffs = None
# constraint_coeffs = [
#     [1, 0],
#     [2, 4],
#     [5, 4],
# ]
# rhs_values = [100, 80, 500]
# rel_coeffs = [">=", "<=", ">="]
# goals = [1, 2, 0]
# maximize = True
#
# tableau = solver.create_tableau(objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, goals)
# error, steps = solver.solve(False, tableau_df=tableau)
# for step in steps:
#     print(step)