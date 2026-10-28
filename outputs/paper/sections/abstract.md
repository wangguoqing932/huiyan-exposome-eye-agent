# Abstract

**Background.** Multi-layer agents that combine deterministic rules, knowledge-graph
retrieval and a language model are inspectable, but whether they outperform
general models, and whether their rules hold elsewhere, are rarely tested together.

**Methods.** Huiyan combines 21 rules, a LightRAG knowledge graph of 1,060 evidence
chunks and an LLM arbiter that returns a source-linked trace. We evaluated
system-level classification against three baselines (internal NHANES, which also
informed rule development; external KNHANES), rule-level direction under a
pre-registered three-state standard (CHARLS; eight ageing cohorts, 285,878
participants), and concordance across four literature indexes. We additionally
audited which evaluation pairs the post-confirmatory rule revision had touched and
repeated the external comparison on the untouched subset.

**Results.** The internal matrix contained no replicated pair that the rule
revision had not touched (0 of 6), so it yields no out-of-sample estimate and is
reported only as a development description (agent F1 0.571 versus rule layer
0.522). Externally, on 301 KNHANES pairs the agent scored 0.375 against 0.360 for
its own deterministic rule layer and 0.176, 0.173 and 0.120 for LightRAG, a pure
LLM and naive RAG. On the 296 pairs untouched by the revision the ordering held
but the level collapsed: 0.211, 0.200, 0.122, 0.089 and 0.086. The agent's
advantage is precision, not recall: it flags 30 of 301 pairs, 9 of them correctly,
and its recall on replicated pairs is 0.500 with a 16.7% flag rate on contradicted
and 7.2% on uninformative pairs. Rule track: only 6 of 21 rules were testable in
the cohorts; of 18 rule x cohort pairs, 8 replicated, 8 were uninformative and 2
contradicted; two met the pre-registered criterion, but both prediction intervals
spanned unity. Literature concordance was 0.889 (PubMed), 0.916 (Web of Science),
0.922 (Europe PMC) and 0.800 (CNKI), with 16/17 cross-index agreement.

**Conclusions.** The agent outperformed LLM and RAG baselines, and narrowly its own
rule layer, on external data, but only a fifth of its external F1 survives when
the pairs that informed development are removed. Its rules were largely untestable
elsewhere (15 of 21), and none was robustly transportable where testable; the
constraint was measurement, not sample size. Agent validation should report
system-level and rule-level results separately, disclose which pairs informed
development, and state which exposures were measured.
