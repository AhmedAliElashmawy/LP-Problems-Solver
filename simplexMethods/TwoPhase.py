import numpy as np
import pandas as pd
import sympy as sp
from .LpInterface import LPSolverInterface


class TwoPhaseSolver(LPSolverInterface):
    def __init__(self):
        self.basic_vars = []
        self.var_names = []
        self.phase_two_obj_coeffs = []
        self.steps = []
        self.answer = None

    def create_tableau(self, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted):
        num_artificial_vars = sum(1 for x in rel_coeffs if x != "≤")
        num_slack_vars = sum(1 for x in rel_coeffs if x != "=")
        num_unrestricted_variables = sum(1 for val in restricted if not val)
        num_constraints, num_variables = len(constraint_coeffs), len(objective_coeffs)
        total_variables = num_variables + num_unrestricted_variables + num_artificial_vars + num_slack_vars
        tableau = sp.zeros(num_constraints + 1, total_variables + 1)

        # Phase 1 Objective Coefficients
        expanded_phase_one_coeffs = [0] * (num_variables + num_unrestricted_variables + num_slack_vars) + [-1] * num_artificial_vars

        # Phase 2 Objective Coefficients
        expanded_phase_two_coeffs = []

        header_row = []
        expanded_constraint_coeffs = []
        artificial_var_id = 1
        slack_var_id = 1
        unrestricted_var_id = 1

        # Step 1: Handle original and unrestricted variables
        for i in range(num_variables):
            if restricted[i]:
                expanded_constraint_coeffs.append([row[i] for row in constraint_coeffs])
                expanded_phase_two_coeffs.append(-objective_coeffs[i])  # Phase 2 objective
                header_row.append(f"x{unrestricted_var_id}")
                unrestricted_var_id += 1
            else:
                expanded_constraint_coeffs.append([row[i] for row in constraint_coeffs])
                expanded_constraint_coeffs.append([-row[i] for row in constraint_coeffs])
                expanded_phase_two_coeffs.append(-objective_coeffs[i])  # Phase 2 objective
                expanded_phase_two_coeffs.append(objective_coeffs[i])  # Phase 2 objective (negative for unrestricted)
                header_row.extend([f"y{unrestricted_var_id}+", f"y{unrestricted_var_id}-"])
                unrestricted_var_id += 1

        expanded_phase_two_coeffs.extend([0]*(num_slack_vars+num_artificial_vars))


        # Step 2: Handle slack variables
        for i in range(len(rel_coeffs)):
            if rel_coeffs[i] == "=":
                continue
            expanded_constraint_coeffs.append([0] * i + [(-1 if rel_coeffs[i] == "≥" else 1)] + [0] * (num_constraints - 1 - i))
            header_row.append(f"s{slack_var_id}")
            slack_var_id += 1

        # Step 3: Handle artificial variables
        for i in range(len(rel_coeffs)):
            if rel_coeffs[i] in ["=", "≥"]:
                expanded_constraint_coeffs.append([0] * i + [1] + [0] * (num_constraints - 1 - i))
                header_row.append(f"a{artificial_var_id}")
                artificial_var_id += 1

        #Handles Basic vars
        artifical_var_id = slack_var_id = 1
        for rel in rel_coeffs:
            self.basic_vars.append(f"a{artifical_var_id}" if rel in ["=", "≥"] else f"s{slack_var_id}")
            if rel in ["=", "≥"]:
                artifical_var_id += 1
            else:
                slack_var_id += 1


        self.phase_two_obj_coeffs= expanded_phase_two_coeffs


        # Fill the tableau with expanded constraint coefficients and RHS values
        tableau[:-1, :total_variables] = sp.Matrix(expanded_constraint_coeffs).T
        tableau[:-1, -1] = sp.Matrix(rhs_values)

        # Set Phase 1 Objective row
        tableau[-1, :total_variables] = sp.Matrix([expanded_phase_one_coeffs])

        self.var_names = header_row + ["RHS"]
        tableau_df = pd.DataFrame(np.array(tableau).astype(object), index=self.basic_vars + ["Z"], columns=self.var_names)

        return tableau_df



    def __phase_one(self, tableau):
        """
        Perform Phase 1 of the Simplex Method with NumPy arrays.
        """
        # Step 1: Add artificial variables to Z row
        artificial_cols = [i for i, name in enumerate(self.var_names) if 'a' in name]
        for col in artificial_cols:
            row_with_a = next(i for i in range(tableau.shape[0]-1) if tableau[i, col] == 1)
            tableau[-1] += tableau[row_with_a]

        self.steps.append(pd.DataFrame(tableau.copy(), index=self.basic_vars + ["Z"], columns=self.var_names))

        while True:
            if abs(tableau[-1, -1]) < 1e-10 and np.max(tableau[-1, :-1]) <= 1e-10:
                break

            # Find entering variable (most positive coefficient in Z row)
            obj_row = tableau[-1, :-1]
            if np.max(obj_row) <= 1e-10:
                break

            pivot_col = np.argmax(obj_row)

            # Find leaving variable using minimum ratio test
            ratios = []
            for i in range(tableau.shape[0]-1):
                if tableau[i, pivot_col] > 1e-10:
                    ratios.append((tableau[i, -1] / tableau[i, pivot_col], i))

            if not ratios:
                print("Phase 1: Unbounded solution")
                return "Phase 1: Unbounded solution" , tableau

            pivot_row = min(ratios, key=lambda x: x[0])[1]
            pivot_element = tableau[pivot_row, pivot_col]

            # Update basic variables
            self.basic_vars[pivot_row] = self.var_names[pivot_col]

            # Perform pivot operation
            tableau[pivot_row] = tableau[pivot_row] / pivot_element
            for i in range(tableau.shape[0]):
                if i != pivot_row:
                    factor = tableau[i, pivot_col]
                    tableau[i] -= factor * tableau[pivot_row]

            self.steps.append(pd.DataFrame(tableau.copy(), index=self.basic_vars + ["Z"], columns=self.var_names))

        # Check feasibility
        if abs(tableau[-1, -1]) > 1e-10:
            print("Infeasible in Phase I")
            return "Infeasible in Phase I" , tableau  # Problem is infeasible

        return False , tableau

    def __phase_two(self, maximize, tableau):
        """
        Perform Phase 2 of the Simplex Method with NumPy arrays.
        """
        # Remove artificial columns
        artificial_cols = [i for i, name in enumerate(self.var_names) if 'a' in name]
        if artificial_cols:
            keep_cols = [i for i in range(tableau.shape[1]) if i not in artificial_cols]
            tableau = tableau[:, keep_cols]
            self.var_names = [name for i, name in enumerate(self.var_names) if i not in artificial_cols]

        # Set up Phase 2 objective function
        tableau[-1] = 0
        for i, col in enumerate(self.var_names[:-1]):  # Exclude RHS
            if col.startswith('x'):
                idx = next((j for j, name in enumerate(self.var_names) if name == col), None)
                if idx is not None and idx < len(self.phase_two_obj_coeffs):
                    coeff = self.phase_two_obj_coeffs[idx]
                    tableau[-1, i] = coeff if maximize else -coeff

        self.steps.append(pd.DataFrame(tableau.copy(), index=self.basic_vars + ["Z"], columns=self.var_names))

        while True:
            # Check optimality
            obj_row = tableau[-1, :-1]
            if maximize:
                if np.min(obj_row) >= -1e-10:
                    break
                pivot_col = np.argmin(obj_row)
            else:
                if np.max(obj_row) <= 1e-10:
                    break
                pivot_col = np.argmax(obj_row)

            # Find leaving variable
            ratios = []
            for i in range(tableau.shape[0]-1):
                if tableau[i, pivot_col] > 1e-10:
                    ratios.append((tableau[i, -1] / tableau[i, pivot_col], i))

            if not ratios:
                print("Unbounded Solution in Phase II")
                return "Unbounded Solution in Phase II" , tableau

            pivot_row = min(ratios, key=lambda x: x[0])[1]
            pivot_element = tableau[pivot_row, pivot_col]

            # Update basic variables
            self.basic_vars[pivot_row] = self.var_names[pivot_col]

            # Perform pivot operation
            tableau[pivot_row] = tableau[pivot_row] / pivot_element
            for i in range(tableau.shape[0]):
                if i != pivot_row:
                    factor = tableau[i, pivot_col]
                    tableau[i] -= factor * tableau[pivot_row]

        self.steps.append(pd.DataFrame(tableau.copy(), index=self.basic_vars + ["Z"], columns=self.var_names))

        # Extract solution
        self.answer = {var: 0 for var in self.var_names[:-1]}
        for i, basic_var in enumerate(self.basic_vars):
            if basic_var in self.answer:
                self.answer[basic_var] = tableau[i, -1]

        return False, tableau

    def solve(self, maximize, tableau_df):
        if tableau_df is None:
            print("Unsolvable with Two-Phase Simplex")
            return "Unsolvable with Two-Phase Simplex", self.steps

        self.steps.append("PHASE I :\n")
        tableau = tableau_df.to_numpy()
        self.var_names = list(tableau_df.columns)
        self.basic_vars = list(tableau_df.index[:-1])
        self.steps.append(tableau_df.copy())

        # Phase 1: Minimize the sum of artificial variables
        error, tableau = self.__phase_one(tableau)

        if(error):
            return error , self.steps

        #Phase 2 :
        self.steps.append("PHASE II :\n")
        error , tableau = self.__phase_two(maximize , tableau)

        return error , self.steps


# solver = TwoPhaseSolver()
# objective_coeffs = [-1, -2 , -1]
# constraint_coeffs = [
#         [1, 1 , 1],
#         [2 , -5 , 1],
#     ]
# rhs_values = [7 , 10]
# rel_coeffs = ["=" , '≥']
# restricted = [True, True , True]
# tableau_df = solver.create_tableau(objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted)
# print("Initial Tableau:")
# print(tableau_df)


# optimal_value, steps = solver.solve(maximize=True, tableau_df=tableau_df)

# print("\nOptimal Value:", optimal_value)
# print("\nSteps:")
# for step in steps:
#     print(step, "\n")







