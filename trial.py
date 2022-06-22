# -*- coding: utf-8 -*-
import fastf1 as ff1
import pandas as pd

# Enable the cache
ff1.Cache.enable_cache('cache')

quali = ff1.get_session(2021, 'Turkey', 'Q')

laps = quali.load_laps(with_telemetry=True)
df = pd.DataFrame(laps)

df = df[['DriverNumber', 'TrackStatus', 'Compound', 'TyreLife', 'FreshTyre', 'LapNumber', 'Stint', 'PitInTime', 'PitOutTime', 'LapTime']]

# ‘1’: Track clear (beginning of session ot to indicate the end of another status)
# ‘2’: Yellow flag (sectors are unknown)
# ‘3’: ??? Never seen so far, does not exist?
# ‘4’: Safety Car
# ‘5’: Red Flag
# ‘6’: Virtual Safety Car deployed
# ‘7’: Virtual Safety Car ending (As indicated on the drivers steering wheel, on tv and so on; status ‘1’ will mark the actual end)
# https://theoehrly.github.io/Fast-F1/api.html#fastf1.api.track_status_data

# PREPROCESSING
df['TyreLife'] = df['TyreLife'].fillna(0)

#0: soft, 1: medium, 2: hard, 3: inter, 4: wet
df['Compound'] = df['Compound'].replace({'SOFT': 0, 'MEDIUM': 1, 'HARD': 2, 'INTERMEDIATE': 3, 'WET': 4})

#0: not fresh, 1: fresh
df['FreshTyre'] = df['FreshTyre'].replace({True: 1, False: 0}) # to use or not to use?

def find_compound(row):
    driver = row['DriverNumber']
    lap = row['LapNumber'] + 1
    compound = df.loc[(df['DriverNumber'] == driver) & (df['LapNumber'] == lap)]['Compound'].iloc[0]
    if not compound == 'UNKNOWN':
        return compound
    else:
        new_row = row.copy()
        new_row['LapNumber'] += 1
        return find_compound(new_row)

#unknown tyre compounds to be updated with the next lap's compound info, if not available, check next one
unknowns = df[df['Compound'] == 'UNKNOWN']
for index, unknown in unknowns.iterrows():
    driver = unknown['DriverNumber']
    lap = unknown['LapNumber']
    compound = find_compound(unknown)
    df['Compound'].iloc[index] = compound

#what to do for stints?
#pitin-pitout-laptime nans?
print()
