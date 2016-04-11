
"""
acs-migration-data-parser.py
---
Script for parsing census data stored in flat .csv to .json for d3.js visualization.

Input format:
Variables in columns, geographies (counties) in rows.
Variable code in row 1, Description in row 2

Output format:

migrationData = {
    "county1": {
        "title": Name, State (Can do this by hand)
        "brackets": [
            {"bracket":"1 - 4","from_in_state":84,"from_out_state":277,"to_in_state":86,"to_out_state":159},
            {"bracket":"5 - 17","from_in_state":243,"from_out_state":429,"to_in_state":137,"to_out_state":345},
            ... (remaining variables)
            ]
    },
    "county2": ... (other counties)
}

CODE DESCRIPTIONS
Codes come in two parts, e.g. HD01_VD01
HD01 = estimate, HD02 = margin of error
VDXX = order of variable (seemingly arbitrary)

Following is also in B07001-label-key.csv
Age bracket     total   same_house  moved_same_county   moved_in_state  moved_in_usa    moved_from_abroad
Total           VD01    VD18    VD34    VD50    VD66    VD82
5 to 17 years   VD04    VD20    VD36    VD52    VD68    VD84
20 to 24 years  VD06    VD22    VD38    VD54    VD70    VD86
30 to 34 years  VD08    VD24    VD40    VD56    VD72    VD88
40 to 44 years  VD10    VD26    VD42    VD58    VD74    VD90
50 to 54 years  VD12    VD28    VD44    VD60    VD76    VD92
60 to 64 years  VD14    VD30    VD46    VD62    VD78    VD94
70 to 74 years  VD16    VD32    VD48    VD64    VD80    VD96

"""


import csv

inflow_data_path = 'data/MT_COUNTIES_ACS_14_5YR_B07001.csv'
inflow_key_path = 'data/B07001-label-key.csv'

processed_data_path = 'data/migration-by-age.json'

# Geographies to include in analysis (MT counties currently)
include_geos = ['30031', # Gallatin
                '30049', # Lewis & Clark
                '30013', # Cascade
                '30063', # Missoula
                '30111', # Yellowstone
                '30029'  # Flathead
                ]


# Collect inflow data
inflow_data = []
with open(inflow_data_path, 'rb') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['GEO.id2'] in include_geos:
            inflow_data.append(row)

# Collect inflow key
inflow_key = []
with open(inflow_key_path, 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        inflow_key.append(row)

# TODO: set this up so it also pulls in outflow data

# NEW:
# Populates output_text with json-formatted string 
# Logic: loops through include_geos list, for each
# matching to row in inflow_data and
# 1) 1) populating title/label fields in json-style and
# 2) using values in inflow_key to pull out/add desired 
# data elements for each county 

output_text = "{\n"
for i, geoid in enumerate(include_geos):
    # Find county in inflow_data that matches current geoid
    county = filter(lambda county: county['GEO.id2'] == geoid, inflow_data)[0]

    output_text += '"county_' + str(i) + '": { \n'
    output_text += '"title": "' + county['GEO.display-label'] + '",\n'
    output_text += '"fips": "' + county['GEO.id2'] + '",\n'
    output_text += '"label": "THIS IS FILLER",\n'
    output_text += '"brackets": [\n'
    # slice excludes header and total rows
    for index, row in enumerate(inflow_key[2:]):
        total_current_pop = county['HD01_' + row[1]]
        from_in_state = county['HD01_' + row[4]]
        from_out_state = int(county['HD01_' + row[5]]) + int(county['HD01_' + row[6]])

        output_text += '{"bracket":"' + row[0] + '",'
        output_text += '"total_current_pop":' + str(total_current_pop) + ','
        output_text += '"from_in_state":' + str(from_in_state) + ','
        output_text += '"from_out_state":' + str(from_out_state) + ''
        
        # Add trailing comma unless on last row
        if (index < len(inflow_key[2:]) - 1)git:
            output_text += '},\n'
        else:
            output_text += '}\n'
    output_text += ']\n},\n'

# -1 cuts off trailing comma and final \n, add final bracket
output_text = output_text[:-2] + '\n}'

print output_text

with open(processed_data_path, 'wb') as f:
    f.write(output_text)


