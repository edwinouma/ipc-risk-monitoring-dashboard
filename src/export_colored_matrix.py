import pandas as pd
import os


def export_colored_classification_matrix(matrix, filepath):
    """
    Export classification matrix to Excel with color formatting.
    """

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with pd.ExcelWriter(filepath, engine="xlsxwriter") as writer:

        matrix.to_excel(writer, sheet_name="Classification")

        workbook = writer.book
        worksheet = writer.sheets["Classification"]

        # Formats
        alarm_format = workbook.add_format({'bg_color': '#FF0000'})
        alert_format = workbook.add_format({'bg_color': '#FFA500'})
        minimal_format = workbook.add_format({'bg_color': '#C6EFCE'})

        nrows, ncols = matrix.shape

        # Apply conditional formatting (exclude index column)
        worksheet.conditional_format(
            1, 1, nrows, ncols,
            {'type': 'text',
             'criteria': 'containing',
             'value': 'Alarm',
             'format': alarm_format}
        )

        worksheet.conditional_format(
            1, 1, nrows, ncols,
            {'type': 'text',
             'criteria': 'containing',
             'value': 'Alert',
             'format': alert_format}
        )

        worksheet.conditional_format(
            1, 1, nrows, ncols,
            {'type': 'text',
             'criteria': 'containing',
             'value': 'Minimal',
             'format': minimal_format}
        )