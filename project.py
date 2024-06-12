import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import pandas as pd


#method to lead relevant data for a county
def return_yearly_data_for_county(file_path, county):
    df = pd.read_csv(file_path)

    county_df = df[df['County'] == county]
    selected_columns = [
        'Avg Temperature (K)',
        'Precipitation (kg m**-2)',
        'Relative Humidity (%)',
        'Vapor Pressure Deficit (kPa)'
    ]
    county_df = county_df[selected_columns]

    #transform the average data to Celsius
    county_df['Avg Temperature (C)'] = county_df['Avg Temperature (K)'] - 273.15
    county_df.drop(columns=['Avg Temperature (K)'], inplace=True)

    return county_df

def dataframe_into_input_lists(dataframe):
    # round to 2 places after the comma to increase performance
    inputs = {
        'temperature': dataframe['Avg Temperature (C)'].round(2).tolist(),
        'precipitation': dataframe['Precipitation (kg m**-2)'].round(2).tolist(),
        'humidity': dataframe['Relative Humidity (%)'].round(2).tolist(),
        'vapor_pressure_deficit': dataframe['Vapor Pressure Deficit (kPa)'].round(2).tolist()
    }
    return inputs


polk_df = return_yearly_data_for_county("filtered_monthly_oregon.csv", "POLK")
print(polk_df.info())

washington_df = return_yearly_data_for_county("filtered_monthly_oregon.csv", "WASHINGTON")


# Helper function to create monthly antecedents
def create_monthly_antecedents(var_name, var_range):
    return [ctrl.Antecedent(np.arange(*var_range), f'{var_name}_{month}') for month in range(1, 13)]


# Define the input variables for each month
temperature = create_monthly_antecedents('temperature', (-30, 51, 0.01))
precipitation = create_monthly_antecedents('precipitation', (0, 41, 0.01))
humidity = create_monthly_antecedents('humidity', (0, 101, 0.01))
vapor_pressure_deficit = create_monthly_antecedents('vapor_pressure_deficit', (0, 2.1, 0.01))


# Define the output variable for yearly yield
yield_tons_per_hectare = ctrl.Consequent(np.arange(0, 18, 0.01), 'yield_tons_per_hectare')

#here we define membership functions for all variables for each month (4x12=48 functions)
for t in temperature:
    t['extremely_low'] = fuzz.trimf(t.universe, [-30, -30, 5])
    t['low'] = fuzz.trimf(t.universe, [0, 5, 15])
    t['medium'] = fuzz.trimf(t.universe, [10, 20, 30])
    t['high'] = fuzz.trimf(t.universe, [25, 50, 50])

# https://disc.gsfc.nasa.gov/information/faqs?title=How%20to%20convert%20the%20rainfall%20unit%20of%20kg%2Fm%5E2%20to%20mm%3F
# here we have the value of the daily average in a month
for p in precipitation:
    p['low'] = fuzz.trimf(p.universe, [0, 0, 2])
    p['medium'] = fuzz.trimf(p.universe, [1, 15, 30])
    p['high'] = fuzz.trimf(p.universe, [20, 40, 40])


for h in humidity:
    h['low'] = fuzz.trimf(h.universe, [0, 0, 40])
    h['medium'] = fuzz.trimf(h.universe, [30, 50, 70])
    h['high'] = fuzz.trimf(h.universe, [60, 100, 100])

# https://pulsegrow.com/blogs/learn/vpd around 0.8 kPa is the most optimal for plants
for v in vapor_pressure_deficit:
    v['low'] = fuzz.trimf(v.universe, [0, 0, 0.6])
    v['medium'] = fuzz.trimf(v.universe, [0.45, 0.8, 1.25])
    v['high'] = fuzz.trimf(v.universe, [1, 2, 2])


# Define membership functions for yield
yield_tons_per_hectare['low'] = fuzz.trimf(yield_tons_per_hectare.universe, [0, 0, 4])
yield_tons_per_hectare['medium'] = fuzz.trimf(yield_tons_per_hectare.universe, [3, 6, 8])
yield_tons_per_hectare['high'] = fuzz.trimf(yield_tons_per_hectare.universe, [7, 10, 13])

rules = []

#here I try to define rules for each month.
#January: Germination and early growth
rules.append(ctrl.Rule(temperature[0]['low'] &
                       precipitation[0]['medium'] &
                       humidity[0]['high'] &
                       vapor_pressure_deficit[0]['low'], yield_tons_per_hectare['high']))
rules.append(ctrl.Rule(temperature[0]['extremely_low'] &
                       precipitation[0]['low'] &
                       humidity[0]['low'] &
                       vapor_pressure_deficit[0]['low'], yield_tons_per_hectare['low']))

#February: Tillering
rules.append(ctrl.Rule(temperature[1]['low'] &
                       precipitation[1]['medium'] &
                       humidity[1]['high'] &
                       vapor_pressure_deficit[1]['low'], yield_tons_per_hectare['high']))
rules.append(ctrl.Rule(temperature[1]['extremely_low'] &
                       precipitation[1]['low'] &
                       humidity[1]['high'] &
                       vapor_pressure_deficit[1]['low'], yield_tons_per_hectare['low']))

#March: Tillering and jointing
rules.append(ctrl.Rule(temperature[2]['low'] &
                       precipitation[2]['medium'] &
                       humidity[2]['medium'] &
                       vapor_pressure_deficit[2]['medium'], yield_tons_per_hectare['high']))
rules.append(ctrl.Rule(temperature[2]['low'] &
                       precipitation[2]['high'] &
                       humidity[2]['high'] &
                       vapor_pressure_deficit[2]['low'],
                       yield_tons_per_hectare['medium']))

#April: Jointing
rules.append(ctrl.Rule(temperature[3]['medium'] &
                       precipitation[3]['medium'] &
                       humidity[3]['medium'] &
                       vapor_pressure_deficit[3]['medium'], yield_tons_per_hectare['high']))
rules.append(ctrl.Rule(temperature[3]['high'] &
                       precipitation[3]['low'] &
                       humidity[3]['low'] &
                       vapor_pressure_deficit[3]['high'], yield_tons_per_hectare['low']))
rules.append(ctrl.Rule(temperature[3]['low'] &
                       precipitation[3]['high'] &
                       humidity[3]['high'] &
                       vapor_pressure_deficit[3]['low'], yield_tons_per_hectare['low']))

#May: Heading
rules.append(ctrl.Rule(temperature[4]['medium'] &
                       precipitation[4]['medium'] &
                       humidity[4]['medium'] &
                       vapor_pressure_deficit[4]['medium'], yield_tons_per_hectare['high']))
rules.append(ctrl.Rule(temperature[4]['medium'] &
                       precipitation[4]['low'] &
                       humidity[4]['low'] &
                       vapor_pressure_deficit[4]['high'], yield_tons_per_hectare['low']))

#June: Flowering
rules.append(ctrl.Rule(temperature[5]['medium'] &
                       precipitation[5]['medium'] &
                       humidity[5]['medium'] &
                       vapor_pressure_deficit[5]['medium'], yield_tons_per_hectare['high']))
rules.append(ctrl.Rule(temperature[5]['high'] &
                       precipitation[5]['low'] &
                       humidity[5]['low'] &
                       vapor_pressure_deficit[5]['high'], yield_tons_per_hectare['low']))
rules.append(ctrl.Rule(temperature[5]['low'] &
                       precipitation[5]['low'] &
                       humidity[5]['low'] &
                       vapor_pressure_deficit[5]['high'], yield_tons_per_hectare['low']))

#July: Grain filling
rules.append(ctrl.Rule(temperature[6]['high'] &
                       precipitation[6]['low'] &
                       humidity[6]['low'] &
                       vapor_pressure_deficit[6]['high'], yield_tons_per_hectare['low']))
rules.append(ctrl.Rule(temperature[6]['medium'] &
                       precipitation[6]['medium'] &
                       humidity[6]['medium'] &
                       vapor_pressure_deficit[6]['medium'], yield_tons_per_hectare['high']))

#August: Grain filling, ripening and Harvest
rules.append(ctrl.Rule(temperature[7]['high'] &
                       precipitation[7]['low'] &
                       humidity[7]['low'] &
                       vapor_pressure_deficit[7]['high'], yield_tons_per_hectare['high']))
rules.append(ctrl.Rule(temperature[7]['medium'] &
                       precipitation[7]['medium'] &
                       humidity[7]['medium'] &
                       vapor_pressure_deficit[7]['medium'], yield_tons_per_hectare['medium']))
rules.append(ctrl.Rule(temperature[7]['low'] &
                       precipitation[7]['high'] &
                       humidity[7]['high'] &
                       vapor_pressure_deficit[7]['low'], yield_tons_per_hectare['low']))

#September: Harvest
rules.append(ctrl.Rule(temperature[8]['high'] &
                       precipitation[8]['low'] &
                       humidity[8]['low'] &
                       vapor_pressure_deficit[8]['high'], yield_tons_per_hectare['high']))
rules.append(ctrl.Rule(temperature[8]['medium'] &
                       precipitation[8]['low'] &
                       humidity[8]['low'] &
                       vapor_pressure_deficit[8]['medium'], yield_tons_per_hectare['medium']))
rules.append(ctrl.Rule(temperature[8]['high'] &
                       precipitation[8]['low'] &
                       humidity[8]['low'] &
                       vapor_pressure_deficit[8]['high'], yield_tons_per_hectare['low']))

#October: Post-harvest, planting
rules.append(ctrl.Rule(temperature[9]['high'] &
                       precipitation[9]['low'] &
                       humidity[9]['low'] &
                       vapor_pressure_deficit[9]['high'], yield_tons_per_hectare['high']))
rules.append(ctrl.Rule(temperature[9]['medium'] &
                       precipitation[9]['medium'] &
                       humidity[9]['medium'] &
                       vapor_pressure_deficit[9]['medium'], yield_tons_per_hectare['medium']))
rules.append(ctrl.Rule(temperature[9]['low'] &
                       precipitation[9]['high'] &
                       humidity[9]['high'] &
                       vapor_pressure_deficit[9]['low'], yield_tons_per_hectare['low']))

#November: Post-planting
rules.append(ctrl.Rule(temperature[10]['medium'] &
                       precipitation[10]['high'] &
                       humidity[10]['high'] &
                       vapor_pressure_deficit[10]['low'], yield_tons_per_hectare['high']))
rules.append(ctrl.Rule(temperature[10]['low'] &
                       precipitation[10]['medium'] &
                       humidity[10]['medium'] &
                       vapor_pressure_deficit[10]['low'], yield_tons_per_hectare['medium']))
rules.append(ctrl.Rule(temperature[10]['extremely_low'] &
                       precipitation[10]['low'] &
                       humidity[10]['low'] &
                       vapor_pressure_deficit[10]['high'], yield_tons_per_hectare['low']))

#December: Dormancy
rules.append(ctrl.Rule(temperature[11]['low'] &
                       precipitation[11]['medium'] &
                       humidity[11]['medium'] &
                       vapor_pressure_deficit[11]['low'], yield_tons_per_hectare['high']))
rules.append(ctrl.Rule(temperature[11]['medium'] &
                       precipitation[11]['high'] &
                       humidity[11]['high'] &
                       vapor_pressure_deficit[11]['low'], yield_tons_per_hectare['medium']))
rules.append(ctrl.Rule(temperature[10]['extremely_low'] &
                       precipitation[10]['low'] &
                       humidity[10]['low'] &
                       vapor_pressure_deficit[10]['high'], yield_tons_per_hectare['low']))


#creating the contrrol system
yield_ctrl = ctrl.ControlSystem(rules)
yield_prediction = ctrl.ControlSystemSimulation(yield_ctrl)

for rule in yield_ctrl.rules:
    print(rule)


def calculate_yield_for_all_counties(county):
    dataframe = return_yearly_data_for_county("filtered_monthly_oregon.csv", county)
    inputs = dataframe_into_input_lists(dataframe)
    for month in range(1, 13):
        yield_prediction.input[f'temperature_{month}'] = inputs['temperature'][month-1]
        yield_prediction.input[f'precipitation_{month}'] = inputs['precipitation'][month-1]
        yield_prediction.input[f'humidity_{month}'] = inputs['humidity'][month-1]
        yield_prediction.input[f'vapor_pressure_deficit_{month}'] = inputs['vapor_pressure_deficit'][month-1]
    yield_prediction.compute()

    output = yield_prediction.output['yield_tons_per_hectare'].round(2)

    # Output the result
    print(f"{county} predicted Yearly Yield: {output} tons per hectare")

    return output


oregon_counties = [
    "BAKER", "BENTON", "CLACKAMAS", "CLATSOP", "COLUMBIA", "COOS", "CROOK", "CURRY",
    "DESCHUTES", "DOUGLAS", "GILLIAM", "GRANT", "HARNEY", "HOOD RIVER", "JACKSON",
    "JEFFERSON", "JOSEPHINE", "KLAMATH", "LAKE", "LANE", "LINCOLN", "LINN", "MALHEUR",
    "MARION", "MORROW", "MULTNOMAH", "POLK", "SHERMAN", "TILLAMOOK", "UMATILLA",
    "UNION", "WALLOWA", "WASCO", "WASHINGTON", "WHEELER", "YAMHILL"
]

outputs = dict()

for county in oregon_counties:
    county_output = calculate_yield_for_all_counties(county)
    outputs[county] = county_output


usda_file = 'USDA_WinterWheat_County_2022.csv'
usda_data = pd.read_csv(usda_file)
oregon_data = usda_data[usda_data['state_name'] == 'OREGON']
oregon_yield = oregon_data[['county_name', 'YIELD, MEASURED IN BU / ACRE']]


#1 bushel/acre  of wheat is approximately 0.0673 tons/hectare
#https://calculator.academy/bushels-per-acre-to-tons-per-hectare-calculator/
oregon_yield['YIELD, MEASURED IN t/ha'] = (oregon_yield['YIELD, MEASURED IN BU / ACRE']*0.0673).round(2)
oregon_yield.drop(columns=['YIELD, MEASURED IN BU / ACRE'], inplace=True)


#we match the value given and calculated
outputs_df = pd.DataFrame(list(outputs.items()), columns=['county_name', 'CALCULATED YIELD'])
merged_df = pd.merge(oregon_yield, outputs_df, on='county_name', how='inner')
print(merged_df)



#now lets create a bar graph, to better visualize the results.
fig, ax = plt.subplots(figsize=(14, 7))

bar_width = 0.35
index = np.arange(len(merged_df))

bar1 = ax.bar(index, merged_df['YIELD, MEASURED IN t/ha'], bar_width, label='Given Yield')
bar2 = ax.bar(index + bar_width, merged_df['CALCULATED YIELD'], bar_width, label='Calculated Yield')

ax.set_xlabel('County Name')
ax.set_ylabel('Yield (t/ha)')
ax.set_title('Given Yield vs Calculated Yield by County')
ax.set_xticks(index + bar_width / 2)
ax.set_xticklabels(merged_df['county_name'], rotation=90)
ax.legend()

plt.tight_layout()
plt.savefig("calculated_yield_plot.png")