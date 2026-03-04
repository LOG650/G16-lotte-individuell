# Proposal LOG650

**Group members:**
Lotte Picard

**Area:**
Operational planning, resource allocation and production planning

**Company (optional):**
The Norwegian Mapping Authority (Kartverket), Regional and Public Contact Division

Background info:

From Kartverket.no:
Geovekst is a collaboration on the establishment, management and use of geographic information. Participants include Kartverket, the Norwegian Public Roads Administration, NVE, Bane NOR, Energi Norge, Telenor, municipalities, county municipalities and the Ministry of Agriculture with its subordinate agencies.
The datasets in FKB consist of, among other things, height, water, land types (AR5), arealbruk (land use), buildings, building structures, lines, roads, railways and airports.
FKB data is non-sensitive and open data. FKB data is financed through the Geovekst collaboration, or by the municipalities alone for municipalities outside Geovekst. FKB data is freely available to Norway digital partners and can be downloaded through the download solution on Geonorge. Private actors must purchase access to the data through a reseller.

From nvdb.no:
The National Road Database (NVDB) is a national service and database from the Norwegian Public Roads Administration. It constitutes the foundation of the Norwegian road system. NVDB contains official information about the road and is used for several purposes.

From SOSI-standardized product specification for FKB-TraktorvegSti 5.1:
FKB-TraktorvegSti is a nationwide, zone-divided FKB dataset containing tractor roads, trails and trailstairs with center line geometry. These are the most detailed data Norway has for such small roads and trails. The data is stored in vector format (curves).
FKB-TraktorvegSti must be seen in connection with the dataset Vegnett (Road Network) which contains the remaining road network and which is managed in the National Road Database (NVDB). Together with the road network from NVDB, FKB-TraktorvegSti should be able to form a complete transport network for drivers, cyclists and pedestrians.
The data basis in FKB-TraktorvegSti will have very varying degrees of network topology. One must expect to do work on connecting FKB-TraktorvegSti and Vegnett before this can be considered one network and used in network analyses.

**Problem Statement:**
The county mapping offices in Kartverket will carry out a quality improvement project for the TraktorvegSti dataset, where the dataset after quality improvement will be implemented in NVDB (National Road Database).

The goal of the quality improvement is for tractor roads and paths to be included together with roads in a national road network for drivers, pedestrians and cyclists.

The quality improvement work is done identically across the country, based on a fixed production line, and involves a good deal of manual editing in the dataset. The work is currently carried out municipality by municipality at the county mapping offices.

Challenges that can affect time consumption are the amount of data that lacks topological consistency or has poor positioning accuracy. In addition, data that is not identifiable in the terrain after control against aerial photos, or that is in conflict with other objects such as buildings and roads, must be removed.

The dataset is stored in zone archives, and each county mapping office is responsible for updates within the municipalities belonging to the county/counties the various offices represent. There is varying capacity at the different mapping offices, and in addition, ongoing and planned mapping projects must be taken into account, where several public actors join forces to finance and produce geographic data.

A mapping project takes place by the data being sent to external companies, which take photos from aircraft, and then construct vector data based on what they see in these aerial photos. During an ongoing mapping project, the data in a delimited area is "locked", i.e., major work there should preferably be avoided while the project is ongoing. This can be a period of half a year or more. Mapping projects mostly take place regionally, with few or many municipalities involved in the same project.

When the mapping offices have finished their work, the data is cleared municipality by municipality to another department in Kartverket, which then performs the entry into NVDB. The delimitation of the project is the part of the production that belongs to the county mapping offices, i.e., the quality improvement job and clearing of municipalities for further entry.

It is a prerequisite that work must be done municipality by municipality with the data, as the entire production line is set up for that.

**Data:**

Workload:

- Number of TraktorvegSti road links per municipality.
- Estimated time consumption per municipality based on history.
- Number of municipalities.

Capacity:

- Number of offices. Kartverket has 10 county mapping offices.
- Local capacity at each mapping office. Varies from office to office.
- Available hours per week/month/season.
- Transfer capacity to NVDB (possibly simulated data). This task is not performed by the county mapping offices.

Geovekst Projects:

- Overview of active projects in municipalities.
- Overview of planned projects.
- Estimated locking period for active and planned projects.

**Decision Variables:**

- Allocation of municipalities to each mapping office.
- Sequence of which municipalities are processed when.
- Resource allocation based on the offices' capacity.
- Adjustments in production sequence due to Geovekst projects.

**Objective Function:**
The goal is to find an organization and distribution of municipalities that:

- Minimizes total project duration for the entire country.
- Utilizes the capacity at the mapping offices in the best possible way.
- To the least extent possible performs quality improvement during periods where municipalities are "locked" due to mapping projects.
- Ensures an even workload.

**Limitations:**

- Different people have different efficiency - we cannot take this into account in the project.
- Mapping projects can change continuously, here time schedules can change.
- All production must be completed municipality by municipality.
