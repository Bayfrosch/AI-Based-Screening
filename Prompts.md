### Usage of AI to further shrink the selection
**For this step, OpenAI GPT-6.1 Sol High was used**

**Prompt 1:**

I am preparing an academic literature review for a seminar paper titled "Threat Modeling with Regard to the Mobility Domain", focusing on privacy in mobility systems. Further Information is in notes.md.

I have four CSV files in the data/ directory, containing approximately 400 research paper records.

Your task is to inspect the datasets and prepare the project for a reproducible literature-screening workflow.

Requirements:
1. Inspect all CSV files programmatically using Python.
2. Identify:
   - Number of records in each file.
   - Available column names and data types.
   - Availability of titles, abstracts, keywords, publication years, authors, and DOIs.
   - Missing or incomplete fields.
   - Potential duplicate records.
3. Identify differences in CSV structure and encoding.
4. Create the directories scripts/, results/, and config/ if necessary.
5. Save a concise dataset report to results/dataset_report.md.
Important:
- Do not print complete datasets or abstracts into the conversation.
- Use Python for data inspection.
- Avoid unnecessary LLM token consumption.
- Do not modify or delete the original CSV files.
- Do not perform semantic screening yet.
At the end, report only a short summary of the dataset structure and potential data-quality problems.

**Prompt 2:**

Using the dataset inspection from Step 1, implement a Python script to clean, normalize, merge, and deduplicate all research paper records.

Requirements:

1. Read all four original CSV files.
2. Normalize column names and map equivalent fields to a common schema.
3. Preserve relevant bibliographic metadata, including titles, abstracts, authors, publication years, DOI, keywords, publication venue, and URLs where available.
4. Preserve the original source file and source row for every record.
5. Normalize DOI values and paper titles for duplicate detection.
6. Identify duplicates using:
   - Exact DOI matches.
   - Exact normalized title matches.
   - Conservative fuzzy title matching for possible duplicates.
7. Automatically merge only high-confidence duplicates.
8. Put uncertain duplicates into a separate review file.
9. Assign a stable unique identifier to every paper.
10. Preserve conflicting metadata and record how duplicates were resolved.

Create:

- `scripts/prepare_dataset.py`
- `results/merged_papers.csv`
- `results/duplicates.csv`
- `results/possible_duplicates.csv`
- `results/cleaning_report.md`

Important:
- Do not delete original CSV files.
- Do not invent missing bibliographic information.
- Do not silently discard metadata.
- Do not perform relevance classification.
- Use deterministic Python code.
- Do not output complete paper records into the conversation.

Make the script reusable and idempotent.

At the end, report the initial number of papers, confirmed duplicates, possible duplicates, and resulting unique records.

**Prompt 3:**

Help me establish explicit and reproducible screening criteria for my academic literature review.

Research topic:
"Threat Modeling with Regard to the Mobility Domain"

Context:
The seminar concerns privacy in mobility systems.

Another seminar topic covers:
"Threat Modeling Frameworks and Privacy Frameworks in the Mobility Domain."

My literature selection should therefore focus on identifying, analyzing, and understanding privacy threats in mobility systems rather than comparing or developing general threat modeling frameworks.

Relevant mobility domains include:
- Connected and autonomous vehicles.
- Vehicle-to-Everything communication (V2X).
- Intelligent transportation systems.
- Public transportation.
- Mobility-as-a-Service (MaaS).
- Ride-sharing and shared mobility.
- Navigation and location-based mobility services.
- Mobility data collection and analysis.

Relevant privacy threats include:
- Location tracking.
- Surveillance.
- Re-identification.
- Trajectory linking.
- Inference attacks.
- Profiling.
- Unauthorized or excessive data disclosure.
- Privacy risks resulting from data aggregation.
- Privacy threats arising from interactions between multiple mobility stakeholders.

Relevant research contributions include:
- Concrete privacy threat models.
- Privacy threat identification and analysis.
- Adversary or attacker models.
- Privacy attack scenarios.
- Architectural privacy risk analysis.
- Empirical evidence of mobility privacy threats.
- Threat-specific mitigation analysis.

Papers whose main contribution is developing or comparing generic privacy or threat modeling frameworks should generally be classified as supporting literature or excluded from the core selection.

However, papers applying frameworks such as LINDDUN or STRIDE to analyze concrete privacy threats in mobility systems should remain eligible.

Your tasks:

1. Create clear inclusion criteria.
2. Create clear exclusion criteria.
3. Define three screening decisions:
   - INCLUDE
   - MAYBE
   - EXCLUDE
4. Define research roles:
   - CORE
   - THREAT_EVIDENCE
   - BACKGROUND
   - MITIGATION
   - FRAMEWORK_FOCUSED
   - OUT_OF_SCOPE
5. Define how uncertain or incomplete abstracts should be handled.
6. Define how foundational papers that are not explicitly about mobility threat modeling should be handled.
7. Define how to prevent false exclusions.

Save the resulting criteria to:
`config/screening_criteria.md`

Do not classify individual papers yet.

Make the criteria sufficiently specific to support consistent screening while avoiding unnecessarily restrictive exclusions.

At the end, summarize the proposed criteria and highlight any ambiguities that may affect screening quality.

**Prompt 4:**

Implement a conservative preliminary literature-screening process using Python.

Input:
- `results/merged_papers.csv`
- `config/screening_criteria.md`

The purpose is to identify clearly irrelevant papers before more expensive semantic evaluation.

Requirements:

1. Implement rule-based screening using titles, abstracts, and keywords.
2. Identify terminology related to:
   - Mobility systems.
   - Location and trajectory data.
   - Privacy threats.
   - Adversary and attack models.
   - Threat analysis.
3. Use keyword groups, synonyms, and phrase matching.
4. Do not require the explicit terms "privacy", "mobility", or "threat modeling" when equivalent concepts appear.
5. Do not automatically exclude papers merely because no keyword matches.
6. Only automatically exclude papers when their available metadata provides clear evidence that they are outside the research scope.
7. Preserve records with missing abstracts or ambiguous relevance for further screening.
8. Record the exact rule and evidence behind each automatic exclusion.

Use these preliminary categories:
- POTENTIALLY_RELEVANT
- UNCERTAIN
- CLEARLY_IRRELEVANT

Create:

- `scripts/preliminary_screening.py`
- `results/preliminary_screening.csv`
- `results/preliminary_screening_report.md`

Important:
- Preserve every paper and its original metadata.
- Do not permanently delete excluded records.
- Prefer retaining irrelevant papers over accidentally excluding relevant research.
- Do not use an LLM for this stage.
- Avoid printing paper abstracts into the conversation.
- Do not impose a target number of remaining papers.

At the end, report the number of records assigned to each category and the reasons for clear exclusions.

**Prompt 5:**
Perform semantic relevance screening of the research papers prepared in the previous steps.

Inputs:
- `results/merged_papers.csv`
- `results/preliminary_screening.csv`
- `config/screening_criteria.md`

Use the screening criteria as the authoritative definition of research relevance.

For every paper requiring semantic evaluation, analyze only:
- Paper ID.
- Title.
- Abstract.
- Keywords, if available.
- Publication year, if available.

Do not read full papers.

For each paper, produce:

1. `decision`: INCLUDE, MAYBE, or EXCLUDE.
2. `research_role`: CORE, THREAT_EVIDENCE, BACKGROUND, MITIGATION, FRAMEWORK_FOCUSED, or OUT_OF_SCOPE.
3. `matched_criteria`: Relevant inclusion or exclusion criterion IDs.
4. `reason`: A concise justification of no more than 25 words.
5. `needs_full_text_review`: true or false.

Classification guidelines:

INCLUDE:
The paper directly investigates privacy threats, threat models, adversaries, attack scenarios, or privacy risks in mobility systems.

MAYBE:
The paper may provide important background, empirical threat evidence, mitigation knowledge, or relevant concepts, but its contribution is not sufficiently clear from the available metadata.

EXCLUDE:
The paper is clearly unrelated to the research objective or primarily addresses another research area.

Important distinctions:
- Privacy threat modeling is the main focus.
- Mobility-specific privacy risks are highly relevant.
- Papers analyzing tracking, trajectory linking, re-identification, and inference attacks may be relevant even without explicitly mentioning threat modeling.
- Papers applying LINDDUN or STRIDE to mobility privacy threats can be highly relevant.
- Papers primarily comparing or developing generic threat modeling frameworks are not core literature.
- Pure cybersecurity papers without a privacy dimension are generally outside scope.

Token-efficiency requirements:

1. Process papers in compact batches of approximately 10–20 records.
2. Never print complete datasets into the conversation.
3. Do not send unnecessary bibliographic metadata to the model.
4. Keep classification explanations short.
5. Use structured JSON for intermediate decisions.
6. Validate output against a defined schema.
7. Save the results of each batch immediately.
8. Make the process resumable.
9. Avoid reprocessing papers that have already been classified.
10. Do not repeatedly include previous screening results in subsequent batches.

If automated model API access is unavailable, use the available Codex session to screen compact batches and save the classifications locally. Do not invent an API connection.

Create:
- `results/semantic_screening.csv`
- `results/included.csv`
- `results/maybe.csv`
- `results/excluded.csv`
- `results/semantic_screening_report.md`

Preserve all original metadata and attach the classifications to the corresponding paper IDs.

Do not invent paper content, research findings, or metadata.

If relevance cannot be established confidently from the abstract, classify the paper as MAYBE rather than excluding it.

Do not impose a predefined number of included papers.

At the end, report the classification totals and the main reasons for exclusion.

**Prompt 6:**

Validate the quality and consistency of the semantic literature-screening results.

Inputs:
- `results/semantic_screening.csv`
- `config/screening_criteria.md`

Tasks:

1. Verify that every unique paper has a screening decision.
2. Check that all decisions use the permitted categories.
3. Check that every classification has a valid justification.
4. Identify inconsistencies between decisions and screening criteria.
5. Identify possible false negatives among excluded papers.
6. Identify papers with missing or insufficient abstracts.
7. Identify similar papers receiving inconsistent classifications.
8. Identify papers that were excluded primarily because they did not explicitly mention "threat modeling".
9. Flag framework-focused papers that nevertheless contain concrete mobility privacy threat analysis.

Create a reproducible validation sample of approximately 30 papers, stratified across INCLUDE, MAYBE, and EXCLUDE.

Save the sample to:
`results/manual_validation_sample.csv`

Include fields where I can enter:
- My classification.
- My research role.
- My comments.

Also create:
`results/validation_report.md`

Do not overwrite existing classifications automatically.

Flag questionable decisions for manual review.

If a completed manual validation file is available, compare my decisions against the automated classifications and calculate agreement statistics and recall where the labeled sample supports it.

Do not calculate recall without manual reference labels.

At the end, provide a concise summary of possible screening problems.

**Prompt 7:**

Prioritize the papers classified as INCLUDE during semantic screening.

Inputs:
- `results/included.csv`
- `results/maybe.csv`
- `config/screening_criteria.md`

The objective is to identify the most useful literature for my seminar paper on privacy threat modeling in mobility systems.

Evaluate each included paper using the available title, abstract, and keywords.

Consider:

1. Direct relevance to privacy threat modeling.
2. Relevance to mobility-specific privacy threats.
3. Depth of adversary, attack scenario, or risk analysis.
4. Specificity of the investigated mobility system.
5. Potential usefulness for explaining concrete privacy threats.
6. Potential usefulness for discussing limitations or open challenges.

Assign a priority:

HIGH:
Directly supports the central research question and should be considered for full-text reading.

MEDIUM:
Provides useful supporting evidence, background, or complementary perspectives.

LOW:
Has limited relevance to the central argument but may be useful as supplementary literature.

Additionally, assign one or more thematic categories:

- Location tracking and surveillance.
- Re-identification.
- Trajectory linking and correlation.
- Inference attacks.
- Connected vehicles and V2X.
- Public transportation and MaaS.
- Mobility-specific threat modeling.
- Privacy risk mitigation.
- Other relevant topics.

Requirements:

- Use only information available in the metadata.
- Do not invent research findings.
- Keep explanations concise.
- Do not rank papers solely by publication year.
- Do not discard foundational research because it is older.
- Do not penalize papers simply because they use threat modeling frameworks.
- Distinguish direct threat analysis from framework evaluation.
- Preserve potentially useful MAYBE papers separately.
- Do not impose an arbitrary limit on the number of HIGH-priority papers.

Create:

- `results/prioritized_papers.csv`
- `results/high_priority.csv`
- `results/medium_priority.csv`
- `results/low_priority.csv`
- `results/prioritization_report.md`

The report should summarize the main research areas represented in the selected literature and identify topics with limited coverage.

At the end, provide a concise overview of the prioritization results.

**Prompt 8:**

Create a structured literature overview from the prioritized research papers.

Inputs:
- `results/prioritized_papers.csv`
- `config/screening_criteria.md`

Research topic:
"Threat Modeling with Regard to the Mobility Domain"

The focus is on privacy threats and threat analysis in mobility systems, not on comparing threat modeling frameworks.

Tasks:

1. Group the papers into thematic research areas.
2. Identify which mobility systems receive the most attention.
3. Identify which privacy threats are most frequently investigated.
4. Identify papers that provide concrete threat models or adversary models.
5. Identify papers that provide empirical evidence of privacy threats.
6. Identify papers that primarily investigate mitigation techniques.
7. Identify apparent gaps in the selected literature.
8. Suggest which papers should be read first.
9. Propose a preliminary structure for my seminar paper based on the selected literature.

Produce the following files:

`results/literature_overview.md`

Include:
- Main research themes.
- Relevant papers for each theme.
- Their potential contribution to the seminar.
- Relationships between themes.
- Preliminary research gaps.
- Recommended reading order.

`results/literature_matrix.csv`

Include:
- Paper ID.
- Title.
- Year.
- Research role.
- Priority.
- Mobility domain.
- Privacy threat categories.
- Research methodology, if identifiable.
- Potential contribution to the seminar.
- Full-text review needed.

`results/paper_outline.md`

Include:
- Suggested research question.
- Preliminary chapter structure.
- Relevant literature for each chapter.
- Topics that should remain outside the paper's main scope.

Important:
- Base all conclusions on available metadata.
- Clearly distinguish abstract-supported findings from tentative interpretations.
- Do not fabricate findings or conclusions.
- Do not claim to have read full papers.
- Do not present publication frequency within this selected dataset as evidence of the entire field's research trends.
- Do not overemphasize framework comparisons.

At the end, summarize the main themes and recommend the 20 most important papers for full-text review.
