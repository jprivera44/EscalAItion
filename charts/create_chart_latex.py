"""Write out (certain laborious) latex commands to include charts in the paper."""

import os

INDEX_TO_CREATE = 1


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


if __name__ == "__main__":
    main()
