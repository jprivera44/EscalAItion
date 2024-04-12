import os



filename_mapping = {
    # Neutral Scenario

    "gpt-3.5_GPT-3.5 Neutral A10_raw.json": "gpt-3.5_Neutral_A10_raw.json",
    "gpt-3.5_GPT-3.5 Neutral A1_raw.json": "gpt-3.5_Neutral_A1_raw.json",
    "gpt-3.5_GPT-3.5 Neutral A2_raw.json": "gpt-3.5_Neutral_A2_raw.json",
    "gpt-3.5_GPT-3.5 Neutral A3_raw.json": "gpt-3.5_Neutral_A3_raw.json",
    "gpt-3.5_GPT-3.5 Neutral A4_raw.json": "gpt-3.5_Neutral_A4_raw.json",
    "gpt-3.5_GPT-3.5 Neutral A5_raw.json": "gpt-3.5_Neutral_A5_raw.json",
    "gpt-3.5_GPT-3.5 Neutral A6_raw.json": "gpt-3.5_Neutral_A6_raw.json",
    "gpt-3.5_GPT-3.5 Neutral A7_raw.json": "gpt-3.5_Neutral_A7_raw.json",
    "gpt-3.5_GPT-3.5 Neutral A8_raw.json": "gpt-3.5_Neutral_A8_raw.json",
    "gpt-3.5_GPT-3.5 Neutral A9_raw.json": "gpt-3.5_Neutral_A9_raw.json",


    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_goals A10_raw.json": "gpt-3.5_no_goals_A10_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_goals A1_raw.json": "gpt-3.5_no_goals_A1_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_goals A20_raw.json": "gpt-3.5_no_goals_A20_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_goals A3_raw.json": "gpt-3.5_no_goals_A3_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_goals A4_raw.json": "gpt-3.5_no_goals_A4_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_goals A5_raw.json": "gpt-3.5_no_goals_A5_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_goals A6_raw.json": "gpt-3.5_no_goals_A6_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_goals A7_raw.json": "gpt-3.5_no_goals_A7_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_goals A8_raw.json": "gpt-3.5_no_goals_A8_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_goals A9_raw.json": "gpt-3.5_no_goals_A9_raw.json",


    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_history A11_raw.json": "gpt-3.5_no_history_A11_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_history A12_raw.json": "gpt-3.5_no_history_A12_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_history A13_raw.json": "gpt-3.5_no_history_A13_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_history A14_raw.json": "gpt-3.5_no_history_A14_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_history A15_raw.json": "gpt-3.5_no_history_A15_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_history A16_raw.json": "gpt-3.5_no_history_A16_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_history A17_raw.json": "gpt-3.5_no_history_A17_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_history A18_raw.json": "gpt-3.5_no_history_A18_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_history A19_raw.json": "gpt-3.5_no_history_A19_raw.json",
    "gpt-3.5_NationConfig#nations_configs_nations_v5_no_history A2_raw.json": "gpt-3.5_no_history_A2_raw.json",

    "gpt-3.5_NoMessage A10_raw.json": "gpt-3.5_NoMessage_A10_raw.json",
    "gpt-3.5_NoMessage A1_raw.json": "gpt-3.5_NoMessage_A1_raw.json",
    "gpt-3.5_NoMessage A2_raw.json": "gpt-3.5_NoMessage_A2_raw.json",
    "gpt-3.5_NoMessage A3_raw.json": "gpt-3.5_NoMessage_A3_raw.json",
    "gpt-3.5_NoMessage A4_raw.json": "gpt-3.5_NoMessage_A4_raw.json",
    "gpt-3.5_NoMessage A5_raw.json": "gpt-3.5_NoMessage_A5_raw.json",
    "gpt-3.5_NoMessage A6_raw.json": "gpt-3.5_NoMessage_A6_raw.json",
    "gpt-3.5_NoMessage A7_raw.json": "gpt-3.5_NoMessage_A7_raw.json",
    "gpt-3.5_NoMessage A8_raw.json": "gpt-3.5_NoMessage_A8_raw.json",
    "gpt-3.5_NoMessage A9_raw.json": "gpt-3.5_NoMessage_A9_raw.json",


    "gpt-3.5_NoPastActions A10_raw.json": "gpt-3.5_NoPastActions_A10_raw.json",
    "gpt-3.5_NoPastActions A1_raw.json": "gpt-3.5_NoPastActions_A1_raw.json",
    "gpt-3.5_NoPastActions A2_raw.json": "gpt-3.5_NoPastActions_A2_raw.json",
    "gpt-3.5_NoPastActions A3_raw.json": "gpt-3.5_NoPastActions_A3_raw.json",
    "gpt-3.5_NoPastActions A4_raw.json": "gpt-3.5_NoPastActions_A4_raw.json",
    "gpt-3.5_NoPastActions A5_raw.json": "gpt-3.5_NoPastActions_A5_raw.json",
    "gpt-3.5_NoPastActions A6_raw.json": "gpt-3.5_NoPastActions_A6_raw.json",
    "gpt-3.5_NoPastActions A7_raw.json": "gpt-3.5_NoPastActions_A7_raw.json",
    "gpt-3.5_NoPastActions A8_raw.json": "gpt-3.5_NoPastActions_A8_raw.json",
    "gpt-3.5_NoPastActions A9_raw.json": "gpt-3.5_NoPastActions_A9_raw.json",

    "gpt-3.5_SysPrompt#freedom A12_raw.json": "gpt-3.5_freedom_A12_raw.json",
    "gpt-3.5_SysPrompt#freedom A15_raw.json": "gpt-3.5_freedom_A15_raw.json",
    "gpt-3.5_SysPrompt#freedom A18_raw.json": "gpt-3.5_freedom_A18_raw.json",
    "gpt-3.5_SysPrompt#freedom A21_raw.json": "gpt-3.5_freedom_A21_raw.json",
    "gpt-3.5_SysPrompt#freedom A24_raw.json": "gpt-3.5_freedom_A24_raw.json",
    "gpt-3.5_SysPrompt#freedom A27_raw.json": "gpt-3.5_freedom_A27_raw.json",
    "gpt-3.5_SysPrompt#freedom A30_raw.json": "gpt-3.5_freedom_A30_raw.json",
    "gpt-3.5_SysPrompt#freedom A3_raw.json": "gpt-3.5_freedom_A3_raw.json",
    "gpt-3.5_SysPrompt#freedom A6_raw.json": "gpt-3.5_freedom_A6_raw.json",
    "gpt-3.5_SysPrompt#freedom A9_raw.json": "gpt-3.5_freedom_A9_raw.json",

    "gpt-3.5_SysPrompt#shutdown A10_raw.json": "gpt-3.5_shutdown_A10_raw.json",
    "gpt-3.5_SysPrompt#shutdown A13_raw.json": "gpt-3.5_shutdown_A13_raw.json",
    "gpt-3.5_SysPrompt#shutdown A16_raw.json": "gpt-3.5_shutdown_A16_raw.json",
    "gpt-3.5_SysPrompt#shutdown A19_raw.json": "gpt-3.5_shutdown_A19_raw.json",
    "gpt-3.5_SysPrompt#shutdown A1_raw.json": "gpt-3.5_shutdown_A1_raw.json",
    "gpt-3.5_SysPrompt#shutdown A22_raw.json": "gpt-3.5_shutdown_A22_raw.json",
    "gpt-3.5_SysPrompt#shutdown A25_raw.json": "gpt-3.5_shutdown_A25_raw.json",
    "gpt-3.5_SysPrompt#shutdown A28_raw.json": "gpt-3.5_shutdown_A28_raw.json",
    "gpt-3.5_SysPrompt#shutdown A4_raw.json": "gpt-3.5_shutdown_A4_raw.json",
    "gpt-3.5_SysPrompt#shutdown A7_raw.json": "gpt-3.5_shutdown_A7_raw.json",


    "gpt-3.5_SysPrompt#simulation A11_raw.json": "gpt-3.5_simulation_A11_raw.json",
    "gpt-3.5_SysPrompt#simulation A14_raw.json": "gpt-3.5_simulation_A14_raw.json",
    "gpt-3.5_SysPrompt#simulation A17_raw.json": "gpt-3.5_simulation_A17_raw.json",
    "gpt-3.5_SysPrompt#simulation A20_raw.json": "gpt-3.5_simulation_A20_raw.json",
    "gpt-3.5_SysPrompt#simulation A23_raw.json": "gpt-3.5_simulation_A23_raw.json",
    "gpt-3.5_SysPrompt#simulation A26_raw.json": "gpt-3.5_simulation_A26_raw.json",
    "gpt-3.5_SysPrompt#simulation A29_raw.json": "gpt-3.5_simulation_A29_raw.json",
    "gpt-3.5_SysPrompt#simulation A2_raw.json": "gpt-3.5_simulation_A2_raw.json",
    "gpt-3.5_SysPrompt#simulation A5_raw.json": "gpt-3.5_simulation_A5_raw.json",
    "gpt-3.5_SysPrompt#simulation A8_raw.json": "gpt-3.5_simulation_A8_raw.json"
}




# Directory where the files are located
directory = 'evals/prompt_ablations_total_files_D21/exponential'

# Renaming files
for old_name, new_name in filename_mapping.items():
    old_path = os.path.join(directory, old_name)
    new_path = os.path.join(directory, new_name)

    # Check if the old file exists
    if os.path.exists(old_path):
        # Rename the file
        os.rename(old_path, new_path)
        print(f"Renamed '{old_name}' to '{new_name}'")
    else:
        print(f"File '{old_name}' does not exist.")

# End of script
print("Done.")


