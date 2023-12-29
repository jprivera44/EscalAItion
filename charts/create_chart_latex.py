"""Write out (certain laborious) latex commands to include charts in the paper."""

import os

import matplotlib as mpl
import pandas as pd

from chart_utils import (
    ALL_DYNAMIC_VARIABLES,
    CHANGETYPE_TO_LABEL,
    DYNAMIC_VARIABLES_TO_CHANGETYPES,
    DYNAMIC_VARIABLES_TO_NAMES,
    ALL_MODEL_NAMES_WITH_GPT_4_BASE,
    ALL_SCENARIOS,
    ALL_NATIONS,
    MODELS_TO_COLORS,
    NATIONS_TO_COLORS,
    SCENARIOS_TO_COLORS,
)

INDEX_TO_CREATE = 5


def main() -> None:
    """Main function."""

    if INDEX_TO_CREATE == 1:
        # Create a big list of figures for all the ./dynamic_variables plots
        buffer = ""
        for i, filename in enumerate(
            [
                name
                for name in os.listdir("charts/dynamic_variables")
                if "Over_Time" in name
            ]
        ):
            assert filename.endswith(".pdf")
            variable = filename.split("_in_")[0].replace("_", " ")
            if i % 3 == 0:
                print(r"\begin{figure*}[ht]")
                buffer = ""
            buffer = (
                (
                    rf"""    \includegraphics[width=\figwidthThreeCol]{{images/dynamic_variables/{filename}}}"""
                )
                + "\n"
                + buffer
            )
            if i % 3 == 2:
                print(buffer.strip("\n"))
                print(
                    rf"""    \caption{{\textbf{{{variable} for each scenario.}}}}
    \label{{fig:dynamic_variables_{variable.replace(" ", "_")}}}
\end{{figure*}}
"""
                )

    elif INDEX_TO_CREATE == 2:
        # Action severities by nation
        for model in ALL_MODEL_NAMES_WITH_GPT_4_BASE:
            for scenario in ALL_SCENARIOS:
                print(
                    rf"""    \includegraphics[width=\figwidthTwoCol]{{images/severity_by_nation/{model}_Action_Severity_Counts_by_Nation_{scenario}_Scenario.pdf}}"""
                )

    elif INDEX_TO_CREATE == 3:
        # Dynamic variables prompt ablation (put territory last)
        for i, dynamic_variable in enumerate(
            ALL_DYNAMIC_VARIABLES[1:] + [ALL_DYNAMIC_VARIABLES[0]]
        ):
            dynamic_variable_pretty = DYNAMIC_VARIABLES_TO_NAMES[
                dynamic_variable
            ].replace(" ", "_")
            print(
                r"""\begin{minipage}{\figwidthTwoColSmaller}""" r"""\begin{figure}[H]"""
            )
            for model in ["GPT-4", "GPT-3.5", "Claude-2.0"]:
                print(
                    rf"""    \includegraphics[width=\figwidthFull]{{images/ablations_dynamic_variables/ablate_var_{dynamic_variable_pretty}_{model}.pdf}}"""
                )
            print(
                f"""    \\caption{{\\textbf{{{dynamic_variable_pretty.replace("_", " ")} prompt ablations.}}}}\n"""
                f"""    \\label{{fig:ablate_var_{dynamic_variable_pretty.lower()}}}\n"""
                r"""\end{figure}"""
                r"""\end{minipage}"""
            )
            if i % 2 == 1:
                print(r"""\clearpage""")

    elif INDEX_TO_CREATE == 4:
        # Colors for nations, models, and scenarios
        for nation_name in ALL_NATIONS:
            print(
                f"\\definecolor{{color{nation_name.lower()}}}{{HTML}}{{{mpl.colors.rgb2hex(NATIONS_TO_COLORS[nation_name])[1:]}}}"
            )
        print()
        for model_name in ALL_MODEL_NAMES_WITH_GPT_4_BASE:
            print(
                f"\\definecolor{{color{model_name.lower().replace('-','')}}}{{HTML}}{{{mpl.colors.rgb2hex(MODELS_TO_COLORS[model_name])[1:]}}}"
            )
        print()
        for scenario_name in ALL_SCENARIOS:
            print(
                f"\\definecolor{{color{scenario_name.lower().replace('-','')}}}{{HTML}}{{{mpl.colors.rgb2hex(SCENARIOS_TO_COLORS[scenario_name])[1:]}}}"
            )

    elif INDEX_TO_CREATE == 5:
        # Table of action impacts on dynamic variables
        action_table = pd.read_csv("action_configs/actions_v8.csv")

        # Print header

        dv_header_line = " & ".join(
            r"\textbf{"
            + DYNAMIC_VARIABLES_TO_NAMES[var].replace("Cybersecurity", "Cyber-security")
            + " ("
            + CHANGETYPE_TO_LABEL[DYNAMIC_VARIABLES_TO_CHANGETYPES[var]]
            + ")}"
            for var in ALL_DYNAMIC_VARIABLES
        )
        print(
            rf"""\begin{{table*}}[ht]
    \centering
    \footnotesize
    \newcolumntype{{L}}{{>{{\raggedright\arraybackslash}}p{{4cm}}}}
    \begin{{tabularx}}{{\textwidth}}{{|L|X|X|X|X|X|X|X|X|X|X|}}
        \toprule
        \textbf{{Action}} & {dv_header_line} \\
        \midrule"""
        )
        for _, row_data in action_table.iterrows():
            row_text = f"""        {row_data["name"]}"""
            for var in ALL_DYNAMIC_VARIABLES:
                changetype = DYNAMIC_VARIABLES_TO_CHANGETYPES[var]
                changetype_col_name = "add" if changetype == "+" else "mult"
                var = var.replace("_dynamic", "").replace("_", " ")
                self_impact = row_data[f"{var}_{changetype_col_name}_self"]
                if var == "nuclear":
                    other_impact = 0
                else:
                    other_impact = row_data[f"{var}_{changetype_col_name}_other"]
                should_include = self_impact != 0 or other_impact != 0
                self_impact = f"+{self_impact}" if self_impact > 0 else self_impact
                other_impact = f"+{other_impact}" if other_impact > 0 else other_impact
                row_text += " & "
                if should_include:
                    row_text += f"{self_impact}"
                    row_text += " / "
                    row_text += f"{other_impact}"
            row_text += r" \\ \hline"
            print(row_text)
        print(
            r"""        \bottomrule
    \end{tabularx}
    \label{{tab:action_impacts}}
\end{table*}"""
        )


if __name__ == "__main__":
    main()
