# Reflection

A website whose sole purpose is to analyze itself.

## Concept

Reflection is a self-referential website — you visit it, interact with it, and those interactions become the data you can explore on the site. It's a mirror. The more people use it, the more interesting the data becomes.

The site exposes its own data infrastructure, modeled after how a real tech company's data stack works — without sharing proprietary details. A live operational database for near real-time event data, and ETL into an analytical layer for heavier queries and historical analysis.

## Why

Real, live behavioral data is hard to find outside of a job. Public datasets are static snapshots. Synthetic data never feels right. Reflection generates real data from real users doing real things — and the thing they're doing is looking at the data.

## Milestones
1. Landing page that logs events data and exposes them to the user. 

Open questions:
- Should the user see only their own events or all events on the website?
- How should the events be exposed? During live interactions (e.g. on-click) or as a stream somewhere?
- What is the functionality needed to make the event stream interesting from an audience perspective? 

2. Meaningful data model 
- Add some basic flows to the website - user sign up, check out / subscribe, review - that make the data more interesting to explore. Ideally, there are multiple types of data created: time series, conversion funnel, natural language, pricing...
- Ensure that the data schema that this will introduce is solid and extensible
- Front end reflects these flows in a way that is interesting for the user to explore

3. Create offline data
- Create a path for the data to move from the online real-time layer to a more analytics-type 
- Be able to explore the offline data myself and convince myself that it's well designed
- Design business pipelines and metrics based on the offline data. Look into the best way to do this: dbt? 

4. Expose an analytics layer on the website
- Navigable UI that helps a user understand the data schema with extensive explanation
- Dashboard with key business metrics
- SQL playground with suggested queries

5. Write-up
- Written posts about the architecture, the art concept, the goal of the website, how to explore the data, example analyses
- Tutorial notebooks (colab?) showing what can be done with the data

## Future Ideas

- Merch store to generate e-commerce and funnel data
- Expose the ETL pipeline itself as content (last snapshot time, rows loaded, transformation logic)
- Open-source the infrastructure code
- Experimentation platform — run A/B tests on the site itself, show results transparently
