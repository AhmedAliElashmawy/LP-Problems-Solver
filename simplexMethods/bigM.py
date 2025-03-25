import numpy as np
import pandas as pd
from .LpInterface import LPSolverInterface
from .simplex import SimplexSolver



class BigMSolver(LPSolverInterface):
    __M = 1e9  # Large constant value instead of symbolic M

    def __init__(self):
        self.basic_vars = []
        self.var_names = []
        self.steps = []
        self.answer = None
        self.simplex_helper = SimplexSolver()


    def create_tableau(self, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted):
        num_artificial_vars = sum(1 for x in rel_coeffs if x != "≤")
        num_slack_vars = sum(1 for x in rel_coeffs if x != "=")
        num_unrestricted_variables = sum(1 for val in restricted if not val)

        num_constraints, num_variables = len(constraint_coeffs), len(objective_coeffs)
        total_variables = num_variables + num_unrestricted_variables + num_artificial_vars + num_slack_vars

        tableau = np.zeros((num_constraints + 1, total_variables + 1))

        artificial_var_id = slack_var_id = unrestricted_var_id = restricted_var_id = 1
        header_row = []
        expanded_obj_coeffs = []
        expanded_constraint_coeffs = []

        # Handles restricted and unrestricted vars
        for i in range(num_variables):
            if restricted[i]:
                expanded_constraint_coeffs.append([row[i] for row in constraint_coeffs])
                expanded_obj_coeffs.append(-objective_coeffs[i])
                header_row.append(f"x{restricted_var_id}")
                restricted_var_id += 1
            else:
                expanded_constraint_coeffs.append([row[i] for row in constraint_coeffs])
                expanded_constraint_coeffs.append([-row[i] for row in constraint_coeffs])
                expanded_obj_coeffs.append(-objective_coeffs[i])
                expanded_obj_coeffs.append(objective_coeffs[i])
                header_row.extend([f"y{unrestricted_var_id}+", f"y{unrestricted_var_id}-"])
                unrestricted_var_id += 1

        # Handles slack variables
        for i in range(len(rel_coeffs)):
            if rel_coeffs[i] == "=":
                continue
            expanded_constraint_coeffs.append([0] * i + [(-1 if rel_coeffs[i] == '≥' else 1)] + [0] * (num_constraints - 1 - i))
            header_row.append(f"s{slack_var_id}")
            slack_var_id += 1
            expanded_obj_coeffs.append(0)

        # Handles artificial variables
        for i in range(len(rel_coeffs)):
            if rel_coeffs[i] in ["=", "≥"]:
                expanded_constraint_coeffs.append([0] * i + [1] + [0] * (num_constraints - 1 - i))
                header_row.append(f"a{artificial_var_id}")
                artificial_var_id += 1
                expanded_obj_coeffs.append(BigMSolver.__M)

        # Handles basic variables
        artificial_var_id = slack_var_id = 1
        for rel in rel_coeffs:
            self.basic_vars.append(f"a{artificial_var_id}" if rel in ["=", "≥"] else f"s{slack_var_id}")
            if rel in ["=", "≥"]:
                artificial_var_id += 1
                slack_var_id+=1
            else:
                slack_var_id += 1

        # Shapes objective row
        expanded_obj_coeffs = [expanded_obj_coeffs]

        # Sets tableau values
        tableau[:-1, :total_variables] = np.array(expanded_constraint_coeffs).T
        tableau[:-1, -1] = np.array(rhs_values)
        tableau[-1, :total_variables] = np.array(expanded_obj_coeffs)

        self.var_names = header_row + ["RHS"]
        return pd.DataFrame(tableau, index=self.basic_vars + ["Z"], columns=self.var_names)

    def solve(self, maximize, tableau_df):
        tableau = tableau_df.copy()

        if not maximize:
            for i, var in enumerate(self.var_names):
                if var.startswith("a"):  # Only modify artificial variable columns
                    tableau.loc["Z", var] = -1 * BigMSolver.__M

        return self.simplex_helper.solve(maximize, tableau)


