# Optimizing Valorant Team Composition with Principal Component Analysis

**LT3 Cayco, Reyes, Uy, Valera**

**Data Mining and Wrangling 1**

**Masters of Science in Data Science**


November 2024

The source code for this project is available on GitHub at [Valorant Agent Analysis Repository](https://github.com/PeteCastle/valorant-agent-analysis)

## Abstract

This research leverages Principal Component Analysis (PCA) to identify key factors contributing to balanced and effective team compositions in the video game Valorant. By analyzing match data, we uncover eight principal components that reveal hidden patterns in player performance, encompassing combat prowess, agent utility usage, and objective play. These findings serve as the foundation of a data-driven framework in agent recommendations based on individual performance profiles and map selection. This research provides insights into player performance with consideration of the dynamic context of Valorant's roster of maps and agent abilities. By empowering players to optimize agent selection and refine their strategies, this research aims to enhance the overall Valorant experience.

## Introduction

Esports have exploded in popularity, fueling the demand for fair and balanced competitive games. Valorant, a free-to-play 5v5 tactical First Person Shooter (FPS) that blends precise gunplay with the unique abilities of playable characters, is the epitome of this trend, which earned it the 2022 Best Esports Game award. 

Two teams of five players face off in a match, taking turns as attackers and defenders. Attackers aim to plant and detonate the Spike, while defenders must stop them or eliminate the entire enemy team. 

The game features an in-game economy system where players purchase weapons and abilities each round, adding strategic depth to gameplay. Different modes and queues offer various gameplay experiences, enumerated below:

*   **Unrated**: A casual 5v5 mode where rank does not matter. The first team to 13 rounds wins.
*   **Competitive**: A ranked 5v5 mode for competitive players. The first team to 13 rounds wins.
*   **Premier**: A team-based competitive tournament mode that lasts for a month, with a focus on organized play. Teams play two games per tournament weekend on a specific map chosen in advance. 
*   **Swift Play**: A shorter version of Unrated, where the first team to 5 rounds wins.
*   **Spike Rush**: A fast-paced mode where all attackers possess the Spike. Players do not purchase weapons but are equipped with randomly assigned loadouts each round. Abilities (excluding ultimate abilities) recharge fully each round.
*   **Deathmatch**: A free-for-all mode focused on individual eliminations. The first player to 40 kills wins.
*   **Team Deathmatch**: A 5v5 team-based deathmatch mode played on specialized maps. A win is determined by either the first team to 100 kills or the team with the most kills by the end of the game. 
*   **Escalation**: A casual mode where teams progress through a series of 12 increasingly unusual weapons. To advance to the next weapon, each player must secure at least one kill with the current weapon, regardless of their team's overall kill count.


## Problem Statement

This study addresses the problem of inadequate player evaluation and agent recommendation in Valorant due to the limitations of traditional performance metrics and the lack of consideration for map-specific factors. 

Traditional evaluations rely heavily on basic statistics like Kills, Deaths, and Assists ratio (KDA), which fail to capture the multifaceted nature of player contributions and their impact on different aspects of the game, especially across the diverse maps in Valorant. This necessitates a more comprehensive understanding of player performance that accounts for individual playstyles, agent abilities, and map interactions. 

Therefore, this study aims to:

1.  Uncover underlying patterns in player performance data using PCA to identify key performance indicators beyond traditional metrics.
2.  Develop a data-driven framework that provides personalized agent recommendations based on individual playstyles, performance profiles, and map selection. 

By addressing these objectives, this study seeks to empower players and analysts with valuable insights and data-driven tools to optimize agent selection, enhance individual performance, and ultimately achieve greater success in Valorant. 


## Motivation

Insights from this analysis can offer substantial benefits to players, Riot Games, and the broader gaming ecosystem. For players and the eSports community, the study provides valuable insights into optimal team composition strategies. Riot Games can utilize these findings to assess the game's health, ensuring a fair and balanced playing field. Additionally, this research encourages the broader gaming community to adopt a data-driven approach to strategize gameplay and assess game health.

## Data Exploration

### Data Source

The Henrikdev API (from [https://docs.henrikdev.xyz/](https://docs.henrikdev.xyz/)) serves as the data source for this analysis due to the limitations of the official Riot Games API. The Henrikdev API provides access to a broader range of Valorant data through various endpoints. These endpoints return data on specific matches, such as: 

*   Game mode, Map, and Player performance 
*   Agent information and their respective abilities 
*   Leaderboard data with rankings and statistics of players in different regions and game modes 
*   Weapon details with statistics and information about the economy in Valorant

This comprehensive data enables a deeper analysis of agent performance and potential imbalances in the game.


### Data Collection

To collect the necessary data for this analysis, a Python script was developed to interact with the Henrikdev API. This script used the requests library to send HTTP requests to various API endpoints, retrieving data on match details, agent information, leaderboards, and weapon statistics. The retrieved data was parsed and stored in JSON format before being loaded into a PostgreSQL database for efficient querying and manipulation. SQL queries were then used to extract relevant information from the 21 tables within the database, ultimately constructing the final dataset for analysis. An Entity Relationship Diagram (ERD) was also created to visualize the relationships between these tables (see Figures 1 and 2). Finally, the processed data was extracted from the SQL database and structured into a Pandas DataFrame for subsequent analysis and visualization in Python.

### Data Cleaning and Preprocessing

The raw data obtained from the Henrikdev API underwent a series of cleaning and preprocessing steps to prepare the data for analysis. Columns that did not directly impact agent abilities from the dataset were removed. The excluded columns consisted of identifiers such as: 

*   **'match\_id'** is a unique identifier for each match. However, the analysis does not use this identifier directly. Instead, relevant player statistics are extracted from each match and linked to the agent used.
*   **'player\_puuid'** is a unique identifier for each player. Including this identifier would introduce unnecessary complexity and potential bias, as individual player skill varies greatly. The analysis focuses on overall agent performance and team composition, not individual player abilities.
*   **'team\_id'** is a unique identifier for each team in a match. This identifier offers no direct insight into agent performance. The analysis examines agent performance independent of team assignment.
*   **'platform'** has the value ‘PC’ as each game was played through a personal computer which is insignificant to analyzing the agent’s performance and winning team composition.
*   **'party\_id'** identifies pre-made groups of players. Including this could introduce bias, as groups often have coordinated strategies and potentially differing skill levels compared to solo players. The analysis aims to assess agent performance independent of these social factors.
*   **'agent\_id'** is a unique identifier for each agent. However, this identifier is unnecessary for the analysis because the data already includes the agent\_name.
*   **‘won’** has boolean values from the match details indicating whether a player won a specific match. However, this column is redundant for the analysis, as the total wins and losses for each agent are already aggregated from the match data.
*   **‘behavior\_rounds\_in\_spawn’, ‘behavior\_afk\_rounds’** track player behavior, specifically whether a player remained in the spawn area or was away-from-keyboard. These behaviors are not relevant to the analysis, as they reflect individual player choices rather than inherent agent abilities.
*   **‘behavior\_friendly\_fire\_incoming’, ‘behavior\_friendly\_fire\_outgoing’** track instances of friendly fire, where players damage their own teammates. These metrics reflect individual player actions and are not relevant to assessing agent balance.
*   **‘session\_playtime\_in\_ms’** measures the total time spent in a match, which does not directly relate to agent performance or balance as other factors may influence the scenario, such as player team composition, latency issues, and other more.

After removing irrelevant columns, the analysis addressed missing values in the remaining data. Rows with null values were removed to ensure data quality. Moreover, the analysis filtered the data using the queue\_id column, retaining only Competitive matches, to ensure the focus on 5v5 game modes, aligning with the objective of identifying effective team compositions within the ranked competitive landscape. Both Premier and Unrated modes were excluded from the analysis as they do not directly contribute to a player's overall rank. Unrated serves as a practice ground for players of all skill levels, while Premier offers a team-based tournament experience.


## Methodology

### Principal Component Analysis

The Valorant match dataset was analyzed using Principal Component Analysis (PCA) to uncover underlying factors that contribute to a balanced team composition. This dimensionality reduction technique transformed the high-dimensional dataset to minimize and retain only most of the original variability while enabling the identification of principal components. These components are combinations of the original features that highlight the most important differences in the data. They effectively summarize the biggest factors that affect how well agents and teams perform. 

The feature columns were assigned as feature variable X, excluding queue ID, map, and agent-specific columns. The resulting dataset comprised 227,121 rows and 30 columns. A correlation matrix was subsequently constructed to explore potential relationships between features, particularly those derived from the original dataset. The correlation matrix identified several strong correlations among features.

### Feature Selection

After performing PCA, the optimal number of features was evaluated. The cumulative variance explained chart indicates that 9 to 12 principal components are required to capture 80\% to 90\% of the variability in the data. However, the scree plot suggests that selecting 6 components might be visually reasonable, though this would explain only 71.8\% of the variability.


To complement these methods, the Kaiser Criterion was applied. This criterion recommends retaining principal components with eigenvalues greater than 1 (Carabidus, 2019). Based on this approach, 8 components were selected, explaining 79.5\% of the variability. This choice strikes a balance between maximizing explained variance and aligning with the visual insights from the scree plot.

## Conclusion

This research addressed the problem of inadequate player evaluation and agent recommendation in Valorant. The study applied PCA to a comprehensive dataset of match data and uncovered hidden patterns. It also identified key performance indicators that go beyond traditional metrics like KDA. These indicators, represented by eight distinct principal components, provide a nuanced understanding of player contributions and playstyles. They encompass combat prowess, agent utility usage, objective play, and map-specific interactions.

The research produced a data-driven framework. This framework offers personalized agent recommendations based on individual performance profiles and map selection. As a result, it empowers players to make informed decisions that maximize their impact and contribute to team success. This framework moves beyond simplistic KDA-based evaluations. It provides a more holistic and insightful understanding of player performance within the dynamic context of Valorant's diverse maps and agent abilities.

Ultimately, this research contributes valuable knowledge to the Valorant community. It offers a data-driven approach to player evaluation and agent recommendation. It equips players and analysts with the tools and insights they need to optimize agent selection, refine strategies, and enhance their overall Valorant experience.

## Recommendation

Based on the identified API limitations and data points not covered by the current analysis, the following recommendations are proposed to enhance the depth and accuracy of future research: 

### API Enhancements:

1.  **Expanded Damage Data:** Request the API to provide more detailed damage data, particularly breakdown by ability and equipment, to gain a more granular understanding of their impact. 
2.  **Comprehensive Post-Round Reports:** Advocate for the inclusion of all post-round reports available in-game within the API to provide a more complete picture of match outcomes. 
3.  **Premade Team Identification:** The data set did not include any indication of whether a team was premade. Explore alternative sources or find a workaround to determine whether a team is premade or not, as this factor can significantly influence team coordination and strategy.
4.  **Privacy Setting Considerations:** Only match details from players with public profiles were analyzed.  Explore potential workarounds or alternative data sources to mitigate the impact of privacy settings and increase the diversity of the dataset, particularly for lower-ranked matches. 
5.  **Crowd Control Data:** Refine data to include information on whether a player was afflicted by crowd control, which causes an agent to slow down or be disarmed, during kill and death scenarios to better assess the impact of these abilities on player performance. 

### Data Analysis Refinements:

1.  **Time Series Analysis:** Implement time series analysis techniques to examine how agent performance varies over the course of a round, especially in relation to Spike plant timings. 
2.  **Economic Impact:** Investigate the influence of economic advantages and disadvantages on team performance and individual player strategies. 
3.  **Ability Usage Analysis:** Develop a more nuanced approach to analyzing ability usage, considering the specific effects and strategic implications of different abilities. 
4.  **Skill Level Impact:** Examine how agent performance varies across different player skill levels to identify agents that are particularly strong or weak in specific ranks. 
5.  **Agent Synergize and Neutralize Analysis:** Certain agents are designed to work well together, and in contrast, certain agents best neutralize the other. Future studies are recommended to incorporate these inherent relationships between agents in identifying effective combinations and team compositions. 

By addressing these limitations and expanding the scope of the analysis, we can gain deeper insights into the factors that contribute to player and team success in Valorant. 

## References

*   Akshon Esports, & Yabumoto, J. (2024, July 29). *Your guide to the 8 VALORANT game modes*. Red Bull. Retrieved from [https://www.redbull.com/ph-en/game-modes-valorant](https://www.redbull.com/ph-en/game-modes-valorant)
*   Carabidus. (2019, February 15). *Principal Component Analysis and Feature Selection*. RPubs. Retrieved from [https://rpubs.com/carabidus/465971](https://rpubs.com/carabidus/465971)
*   Henley, S. (2020, June 4). *Valorant Haven map guide: General tips & Spike sites*. Red Bull. Retrieved November 26, 2024, from [https://www.redbull.com/ca-en/valorant-haven-map-tips-guide](https://www.redbull.com/ca-en/valorant-haven-map-tips-guide)
*   ProGuides. (n.d.). *The complete guide to finding your VALORANT role*. ProGuides. Retrieved November 23, 2024, from [https://www.proguides.com/guides/valorant/the-complete-guide-to-finding-your-valorant-role/#:~:text=There%20are%20four%20different%20roles,the%20pace%20of%20the%20game](https://www.proguides.com/guides/valorant/the-complete-guide-to-finding-your-valorant-role/#:~:text=There%20are%20four%20different%20roles,the%20pace%20of%20the%20game)
*   Teixeira, M. (2024, June 11). *Valorant Bind map guide*. Red Bull. Retrieved November 26, 2024, from [https://www.redbull.com/ph-en/valorant-bind-map-guide](https://www.redbull.com/ph-en/valorant-bind-map-guide)
