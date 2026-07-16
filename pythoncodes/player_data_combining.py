import pandas as pd, glob

# 1. gather the 15 team files (exclude the stray ipl_players_data.csv — see note)
team_files = sorted(f for f in glob.glob('*_players_[dD]ata.csv') if not f.startswith('ipl'))
print(f"Combining {len(team_files)} team files")

# 2. concat — all share the same 38-column schema
players = pd.concat([pd.read_csv(f) for f in team_files], ignore_index=True)
print(f"Raw combined rows: {len(players)}")

# 3. dedup player-seasons.
#    Players who played for multiple franchises appear in multiple files.
#    The only cross-file differences are scrape-time fields (age, t20_end, odi_end),
#    so keep='first' loses no real stats.
players = (players
        .drop_duplicates(subset=['player_id', 'year'], keep='first')
        .reset_index(drop=True))
print(f"After dedup: {len(players)} player-seasons, {players['player_id'].nunique()} players")

players.to_csv('all_players_combined.csv', index=False)