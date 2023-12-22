"""Write out (certain laborious) latex commands to include charts in the paper."""

import os

from chart_utils import (
    ALL_DYNAMIC_VARIABLES,
    DYNAMIC_VARIABLES_TO_NAMES,
    ALL_MODEL_NAMES_WITH_GPT_4_BASE,
    ALL_SCENARIOS,
)

INDEX_TO_CREATE = 3


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


if __name__ == "__main__":
    main()
