import numpy as np
import pandas as pd
from .LpInterface import LPSolverInterface
from .simplex import SimplexSolver


class GoalProgrammingValueSolver(LPSolverInterface):
    def __init__(self):
        self.basic_vars = []
        self.var_names = []
        self.steps = []
        self.answer = None
        self.simplex_helper = SimplexSolver()

    def create_tableau(self, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, goals):

        if constraint_coeffs:
            num_constraints, num_variables = len(constraint_coeffs), len(constraint_coeffs[0])
        else:
            num_constraints, num_variables = 0, 0

        num_slack_vars = sum(1 for goal in goals if goal == 0)  # Slack variables count
        num_deviation_vars = sum(2 if goal != 0 else 0 for goal in goals)  # Deviation vars count
        total_variables = num_variables + num_slack_vars + num_deviation_vars

        # Create empty tableau
        tableau = np.zeros((num_constraints + 1, total_variables + 1))

        var_names = []
        expanded_constraint_coeffs = [[] for _ in range(num_constraints)]
        expanded_objective_coeffs = []
        deviation_vars = []
        slack_vars = []

        # Process normal variables (x1, x2, ...)
        for i in range(num_variables):
            var_names.append(f"x{i + 1}")

            # Add variable coefficients to each constraint row
            for j in range(num_constraints):
                expanded_constraint_coeffs[j].append(constraint_coeffs[j][i])

            expanded_objective_coeffs.append(0)  # Decision variables do not contribute to the objective

        # Process slack and deviation variables
        deviation_index = 0

        for i in range(num_constraints):
            if goals[i] == 0:  # If no goal, use slack variable
                slack_var = f"S{i + 1}"
                slack_vars.append(slack_var)
                var_names.append(slack_var)

                # Insert slack variable into constraints
                for j in range(num_constraints):
                    expanded_constraint_coeffs[j].append(1 if j == i else 0)

                expanded_objective_coeffs.append(0)  # Slack does not affect objective

            else:  # Use deviation variables (d+, d-)
                deviation_vars.append(f"d{i + 1}+")
                deviation_vars.append(f"d{i + 1}-")
                var_names.extend([f"d{i + 1}+", f"d{i + 1}-"])

                # Insert deviation variables into constraints
                for j in range(num_constraints):
                    if j == i:
                        expanded_constraint_coeffs[j].append(-1)  # d+
                        expanded_constraint_coeffs[j].append(1)  # d-
                    else:
                        expanded_constraint_coeffs[j].append(0)
                        expanded_constraint_coeffs[j].append(0)

                # Add to objective function
                if rel_coeffs[i] == "≤":
                    expanded_objective_coeffs.append(goals[i])  # d+ contributes positively
                    expanded_objective_coeffs.append(0)

                elif rel_coeffs[i] == "≥":
                    expanded_objective_coeffs.append(0)
                    expanded_objective_coeffs.append(goals[i])  # d- contributes negatively

                else:  # Assuming "=" case
                    expanded_objective_coeffs.append(goals[i])  # d+ contributes positively
                    expanded_objective_coeffs.append(goals[i])  # d- contributes negatively

                deviation_index += 2

        # Convert expanded constraints to numpy array
        expanded_constraint_coeffs = np.array(expanded_constraint_coeffs)

        # Fill the tableau with constraint coefficients
        tableau[:-1, :expanded_constraint_coeffs.shape[1]] = expanded_constraint_coeffs

        # Add RHS values
        tableau[:-1, -1] = rhs_values

        # Add objective function coefficients
        tableau[-1, :len(expanded_objective_coeffs)] = -1 * np.array(expanded_objective_coeffs)

        # Add variable names
        var_names.append("RHS")
        self.var_names = var_names

        # Assign basic variables (always d- if present, otherwise S)
        self.basic_vars = [
            f"d{i + 1}-" if f"d{i + 1}-" in deviation_vars else f"S{i + 1}" for i in range(num_constraints)
        ]
        return pd.DataFrame(tableau, index=self.basic_vars + ["Z"], columns=self.var_names)

    def solve(self, maximize, tableau_df):
        return self.simplex_helper.solve(maximize=False, tableau_df=tableau_df)


