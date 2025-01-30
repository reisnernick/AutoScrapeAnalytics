import pandas as pd
import os

# Lokalen Pfad der .py-Datei bestimmen
script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, 'autoscout24_vehicles.csv')

# CSV-Datei einlesen
df = pd.read_csv(input_file, delimiter=';', encoding='utf-8')

# Konvertiere die "Year"-Spalte in datetime-Format
df['Year'] = pd.to_datetime(df['Year'], errors='coerce')


# Schritt 1: Generation definieren
def categorize_generation(row):
    year = row['Year']
    if pd.Timestamp('2014-01-01') <= year <= pd.Timestamp('2018-10-01'):
        return '1. Gen'
    elif year > pd.Timestamp('2018-10-01'):
        return '2. Gen'
    else:
        return 'Unbekannt'

# Anwenden der Funktion auf den DataFrame
df['Generation'] = df.apply(categorize_generation, axis=1)

# Schritt 6: Kombiniere Model und Generation zu einer neuen Spalte
df['Model_Gen'] = df['Model'] + ' - ' + df['Generation']

# Speichern der Datei im lokalen Skript-Pfad
output_file = os.path.join(script_dir, 'autoscout24_vehicles_generation.csv')
df.to_csv(output_file, index=False, sep=';', encoding='utf-8')

print(f"Datei gespeichert unter: {output_file}")
