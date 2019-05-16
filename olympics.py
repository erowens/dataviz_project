import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

olympics = pd.read_csv('olympics/athlete_events.csv', index_col=0)


# Bubble Map

sport_games_cts = olympics.groupby('Sport').nunique().Games
sport_games_cts = sport_games_cts[sport_games_cts>=2]
sport_index = olympics.set_index('Sport')
olympics_refined = sport_index.loc[sport_games_cts.index]
golds = olympics_refined[olympics_refined.Medal=='Gold']
sport_golds = golds.groupby(['Sport', 'NOC']).count().Medal

sports = []
top_countries = []
for sport in sport_golds.index.levels[0]:
    sport_gold_count = sport_golds.loc[sport]
    sports.append(sport)
    top_countries.append(sport_gold_count.idxmax())

top_countries = ['RUS' if country == 'URS' else country for country in top_countries]
country_sports = pd.Series(sports, index=top_countries)
countries = []
sport_strings = []
sport_cts = []
for country in country_sports.index.unique():
    country_sport = country_sports.loc[country]
    if type(country_sport) == str:
        sport_strings.append(country_sport)
        sport_cts.append(1)
    else:
        all_sports = ', '.join(country_sport.values)
        sport_strings.append(all_sports)
        sport_cts.append(country_sport.shape[0])
    countries.append(country)

final_info = pd.DataFrame([sport_cts, sport_strings], columns=countries, index=['count', 'string']).transpose()
final_info.to_csv('country_cts.csv')


# Boxplot

only_summer_golds = olympics[(olympics.Medal == 'Gold') & (olympics.Season == 'Summer')]

class smart_dict(dict):
    def __missing__(self, key):
        return key

only_summer_golds['NOC'] = only_summer_golds.NOC.map(smart_dict({'URS':'RUS', 'GDR':'GER'})).copy()
country_gold_cts = only_summer_golds.groupby(['NOC', 'Games']).nunique().Event
top15 = country_gold_cts.groupby(['NOC']).sum().sort_values(ascending=False).iloc[:15]
top15_golds = country_gold_cts.loc[top15.index].reset_index()

nation_colors = ['#00843D',  # AUS
                 '#aa381e',  # CHN
                 '#b5c9d8',  # FIN
                 '#0072bb',  # FRA
                 '#001F7E',  # GBR
                 '#FFCE00',  # GER
                 '#436F4D',  # HUN
                 '#009246',  # ITA
                 '#bc002d',  # JPN
                 '#0047A0',  # KOR
                 '#FFA500',  # NED
                 '#FCD116',  # ROU
                 '#D52B1E',  # RUS
                 '#fecc00',  # SWE
                 '#3C3B6E',  # USA
                ]

plt.figure(figsize=(10,6))
sns.boxplot(data=top15_golds, x='NOC', y='Event', palette=nation_colors)
plt.title('Distribution of Gold Medals Won at Summer Olympics')
plt.xlabel('Nation')
plt.ylabel('Gold Medal Count')
plt.show()


# Histogram

athletics = olympics[(olympics.Sport == 'Athletics') & (olympics.Year >= 2000)]
athletics_medals = athletics[1-athletics.Medal.isna() == 1]
country_athletics_medals = athletics_medals.groupby(['NOC', 'Year']).Event.nunique()

plt.figure(figsize=(10,6))
plt.hist(country_athletics_medals.groupby(['NOC']).sum()/5)
plt.title('Distribution of Athletics Medals Won per Olympics Since 2000')
plt.xlabel('Medals Won')
plt.ylabel('Country Count')
plt.show()


# Barplot

phelps = olympics[olympics.Name == 'Michael Fred Phelps, II']
phelps.fillna('None', inplace=True)
phelps_byyear = phelps.groupby(['Year', 'Medal']).Event.nunique()

medal_ct = []
years = []
medals = []
for year in phelps_byyear.index.levels[0]:
    for medal in phelps_byyear.index.levels[1]:
        if medal in phelps_byyear.loc[year]:
            medal_ct.append(phelps_byyear.loc[year].loc[medal])
        else:
            medal_ct.append(0)
        years.append(year)
        medals.append(medal)

full_phelps = pd.DataFrame({'Year':years, 'Medal_ct':medal_ct}, index=medals)

plt.figure(figsize=(10,6))
bar_Gold = plt.bar(full_phelps.loc['Gold'].Year, full_phelps.loc['Gold'].Medal_ct, color='gold', width=2)
bar_Silver = plt.bar(full_phelps.loc['Silver'].Year, full_phelps.loc['Silver'].Medal_ct, 
                     bottom=full_phelps.loc['Gold'].Medal_ct, color='Silver', width=2)
bar_Bronze = plt.bar(full_phelps.loc['Bronze'].Year, full_phelps.loc['Bronze'].Medal_ct, 
                     bottom=full_phelps.loc['Gold'].Medal_ct.values+full_phelps.loc['Silver'].Medal_ct.values,
                    color='#cd7f32', width=2)
bar_None = plt.bar(full_phelps.loc['None'].Year, full_phelps.loc['None'].Medal_ct, 
                   bottom=full_phelps.loc['Gold'].Medal_ct.values+full_phelps.loc['Silver'].Medal_ct.values+
                  full_phelps.loc['Bronze'].Medal_ct.values, color='Red', width=2)

plt.xticks([2000, 2004, 2008, 2012, 2016])
plt.legend((bar_None[0], bar_Bronze[0], bar_Silver[0], bar_Gold[0]), ('No Medals', 'Bronze', 'Silver', 'Gold'),
          bbox_to_anchor=(1,1))
plt.title("Michael Phelps' Outcomes at the Olympics")
plt.xlabel('Year')
plt.ylabel('Event Count')
plt.show()


# Heat Map

sport_sample = ['Athletics', 'Gymnastics', 'Swimming', 'Rowing', 'Wrestling', 'Weightlifting',
                'Cross Country Skiing', 'Alpine Skiing', 'Speed Skating', 'Figure Skating']
sport_binary = [True if sport in sport_sample else False for sport in olympics.Sport]
select_sports = olympics[sport_binary & (olympics.Medal=='Gold')]
select_sports['NOC'] = select_sports.NOC.map(smart_dict({'URS':'RUS', 'GDR':'GER'}))
country_full_cts = select_sports.groupby(['NOC', 'Games', 'Sport']).Event.nunique().reset_index()
top_countries = top15_golds.NOC.unique()
country_sport_cts = country_full_cts.groupby(['Sport','NOC']).Event.sum()

full_data = []
for sport in sport_sample:
    sport_data = country_sport_cts.loc[sport]
    tot = sum(sport_data)
    sport_list = []
    for country in top_countries:
        if country in sport_data.index:
            country_sport = sport_data.loc[country]
            sport_list.append(country_sport/tot)
        else:
            sport_list.append(0)
    full_data.append(sport_list)

matrix = pd.DataFrame(full_data, index=sport_sample, columns=top_countries)

plt.figure(figsize=(10,6))
ax = sns.heatmap(matrix, linewidth=0.5, cmap='hot')
plt.title('Percentage of Golds Won in Select Sports')
# plt.xlabel('Country')
# plt.ylabel('Sport')
plt.show()


# Choropleth

south_american = ['ARG', 'BOL', 'BRA', 'CHI', 'COL', 'ECU', 'GUY', 'PAR',
                 'PER', 'SUR', 'URU', 'VEN']
south_american_data = olympics[[True if country in south_american else False for country in olympics.NOC]]
south_american_data.fillna('None', inplace=True)
south_american_data = south_american_data[south_american_data.Medal != 'None']
sa_medal_cts = south_american_data.groupby(['NOC', 'Games', 'Medal']).Event.nunique().reset_index()
sa_medal_cts.groupby(['NOC']).Event.sum().to_csv('south_america.csv')


# Connection Map

host_cities = olympics.groupby('Games').City.unique()
host_cities_full = pd.DataFrame([value.split() for value in host_cities.index.values], columns=['Year', 'Games'])
host_cities_full['City'] = [array[0] for array in host_cities]
host_cities_full.sort_values(['Games', 'Year']).to_csv('connection.csv')


# Stream graph

regions = pd.read_csv('olympics/noc_regions.csv', index_col=0)
region_dict = {noc:regions.continent.loc[noc] for noc in regions.index}
olympics['continent'] = olympics.NOC.map(region_dict)
olympics[olympics.Season=='Summer'].groupby(['Year', 'continent']).Name.nunique().to_csv('stream.csv')


# Treemap

all_years = olympics[(olympics.Season=='Winter') & (olympics.Medal=='Gold')].groupby(['Year', 'continent', 'NOC']).Event.nunique()
all_years = all_years.reset_index()
all_years['NOC'] = all_years.NOC.map(smart_dict({'GDR':'GER', 'URS':'RUS'}))
all_years.groupby(['continent', 'NOC']).Event.sum().to_csv('treemap.csv')


# Scatterplot

population = pd.read_excel('world_pop2.xlsx', index_col=0)
pop_2015 = population[2015]
country_golds = olympics[(olympics.Year>=2000) & (olympics.Medal=='Gold')].groupby(['NOC', 'Games']).Event.nunique()
country_golds_tot = country_golds.reset_index().groupby('NOC').sum()

country_codes = {noc:regions.region.loc[noc] for noc in regions.index}
region_dict = {noc:regions.continent.loc[noc] for noc in regions.index}
continent_map = {'africa':'Africa', 'asia':'Asia', 'northam':'North America',
                'europe':'Europe', 'southam':'South America', 'oceania':'Oceania'}

country_golds_tot['country'] = country_golds_tot.index.map(country_codes)
country_golds_tot['continent'] = country_golds_tot.index.map(region_dict)
country_golds_tot.set_index('country', inplace=True)

country_gold_popn = country_golds_tot.join(pop_2015, how='outer')
country_gold_popn = country_gold_popn[(country_gold_popn.Event>0)]

plt.figure(figsize=(10,6))
axes = []
continents = []
for continent in country_gold_popn.continent.unique():
    if continent not in ['none', np.nan]:
        continent_golds = country_gold_popn[country_gold_popn.continent==continent]
        axes.append(plt.scatter(np.log10(continent_golds[2015]*1000), continent_golds.Event))
        continents.append(continent_map[continent])
plt.title('Population vs. Olympic Gold Medals Since 2000')
plt.xlabel('Population (Log Scale)')
plt.ylabel('Gold Medals Won')
plt.legend(axes, continents, bbox_to_anchor=(1,1))
plt.show()


# Storyline Scatterplot

gdp = pd.read_excel('gdp.xlsx', index_col=4)
country_gold_gdp = country_golds_tot.join(gdp, how='outer')
country_gold_gdp = country_gold_gdp[(country_gold_gdp.Event>0)]

plt.figure(figsize=(10,6))
axes = []
continents = []
for continent in country_gold_gdp.continent.unique():
    if continent not in ['none', np.nan]:
        continent_golds = country_gold_gdp[country_gold_gdp.continent==continent]
        axes.append(plt.scatter(np.log10(continent_golds.unGDP), continent_golds.Event))
        continents.append(continent_map[continent])
plt.title('GDP vs. Olympic Gold Medals Since 2000')
plt.xlabel('GDP (Log Scale)')
plt.ylabel('Gold Medals Won')
plt.legend(axes, continents, bbox_to_anchor=(1,1))
plt.show()
