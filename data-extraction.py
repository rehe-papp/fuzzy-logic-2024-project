import pandas as pd


#code to extract the monthly data from all the .csv files

combined_df = pd.DataFrame()

for i in range(1, 13):
    if i > 9:
        file_path = f"OR/HRRR_41_OR_2022-{i}.csv"
    else:
        file_path = f"OR/HRRR_41_OR_2022-0{i}.csv"
    df = pd.read_csv(file_path)

    monthly_df = df[df['Daily/Monthly'] == 'Monthly']

    combined_df = pd.concat([combined_df,monthly_df])

output_file = "filtered_monthly_oregon.csv"
combined_df.to_csv(output_file, index=False)