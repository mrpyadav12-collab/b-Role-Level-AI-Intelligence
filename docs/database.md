# Database design

## Core idea
The application uses a relational data model to represent the real structure of work.

Role -> Process -> Activity -> Skill

## Main tables
- organizations
- roles
- processes
- role_processes
- activities
- skills
- activity_skills
- ai_capabilities
- research_evidence
- activity_assessments
- role_profiles

## Representation
A role owns multiple processes. Each process contains activities. Each activity has related skills. This allows the analysis to be grounded in actual work rather than only in a headline role description.

## Why this structure was chosen
- keeps facts separate from AI interpretation
- supports explainability
- enables caching and scale
- works well with SQLite

## Indexes and performance
The schema includes indexes on role, process, activity, and assessment lookups to minimize repeated scans.

## Example relationship
A role like Bank Teller has multiple processes such as Counter Transaction Processing and Customer Servicing. Each process contains activities like checking identity documents or answering routine account queries. These activities are linked to skills like Data Entry, Compliance Monitoring, and Communication.
