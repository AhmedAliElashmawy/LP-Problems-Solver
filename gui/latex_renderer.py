import matplotlib.pyplot as plt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import io

class LatexRenderer:
    @staticmethod
    def render_lp_problem(problem_type, obj_terms, constraints):
        # Build the objective string.
        objective = " + ".join(obj_terms)
        # Remove "subject to" if there are no constraints
        if not constraints:
            header = r"$\text{" + problem_type.capitalize() + r"}\quad Z = " + objective + r"$"
        else:
            header = r"$\text{" + problem_type.capitalize() + r"}\quad Z = " + objective + r"\quad \text{subject to:}$"
        
        # Build constraint lines.
        constraint_texts = []
        if constraints:
            for constraint in constraints:
                constraint_texts.append(r"$" + constraint + r"$")
        
        # Calculate figure height based on the number of text lines
        num_lines = 1 + len(constraint_texts)
        fig_height = 0.8 + 0.2 * len(constraint_texts)  # Increased base height and spacing
        
        # Create a figure with no axes
        fig, ax = plt.subplots(figsize=(6, fig_height), dpi=150)
        ax.set_axis_off()
        
        # Use normalized coordinates (0 to 1); start at the top
        y_pos = 0.95
        ax.text(0.5, y_pos, header, fontsize=12, ha='center', va='top', color='white')
        
        # Render each constraint on its own line
        for line in constraint_texts:
            y_pos -= 0.25 
            ax.text(0.5, y_pos, line, fontsize=12, ha='center', va='top', color='white')
        
        # Save the figure to an in-memory buffer as PNG with a transparent background.
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
        buf.seek(0)
        img = QImage()
        img.loadFromData(buf.getvalue())
        pixmap = QPixmap.fromImage(img)
        
        plt.close(fig)
        return pixmap
