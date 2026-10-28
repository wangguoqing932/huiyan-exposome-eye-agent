# Abstract

**Background.** Multi-layer agents that combine deterministic rules, knowledge-graph
retrieval and a language model are inspectable, but whether they outperform
general models, and whether their rules hold elsewhere, are rarely tested together.

**Methods.** Huiyan combines 21 rules, a LightRAG knowledge graph of 1,060 evidence
chunks and an LLM arbiter that returns a source-linked trace. We evaluated
system-level classification of the deployable agent against three baselines
(internal NHANES, which also informed rule development; external KNHANES),
rule-level direction under a pre-registered three-state standard (CHARLS; eight
ageing cohorts, 285,878 participants), and concordance across four literature indexes.

**Results.** System track: internally the agent reached F1 0.571 (80 pairs;
LightRAG 0.392, pure LLM 0.335, naive RAG 0.080) and 0.522 (159 pairs; 0.186,
0.178, 0.069). That matrix is in-sample: the rule set was revised after the first
confirmatory run, so recall of 1.000 is a property of that revision (the
pre-revision set scored 0.111). Externally (KNHANES, 301 pairs) the same agent
scored 0.312 against 0.145, 0.135 and 0.094, but below its deterministic rule
layer (0.360): the gates raised precision (0.281 to 0.357) and halved recall
(0.500 to 0.278). Under a binary collapse, sensitivity was 1.00 internally and
0.278 externally, with external specificity 0.968 and kappa 0.275. Rule track:
only 6 of 21 rules were testable in the cohorts; of 18 rule x cohort pairs,
8 replicated, 8 were uninformative and 2 contradicted; two met the pre-registered
criterion but both intervals spanned unity. Literature concordance was 0.889
(PubMed), 0.916 (Web of Science), 0.922 (Europe PMC) and 0.800 (CNKI), with
16/17 cross-index agreement.

**Conclusions.** The agent outperformed LLM and RAG baselines on two national
surveys and returned a source-linked report through a working interface, yet on
independent data it did not outperform its own deterministic rule layer. Its rules
were largely untestable elsewhere (15 of 21), and none was robustly transportable
where testable; the constraint was measurement, not sample size. Agent validation
should report system-level and rule-level results separately, state whether the
benchmark informed development, and state which exposures were measured.
