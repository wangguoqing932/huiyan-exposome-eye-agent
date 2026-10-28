# Abstract

**Background.** Multi-layer agents combining deterministic rules, knowledge-graph
retrieval and a language model are inspectable, but whether they outperform
general models and whether their rules hold elsewhere are rarely tested together.

**Methods.** Huiyan combines 21 rules, a LightRAG knowledge graph of 1,060 evidence
chunks and an LLM arbiter that returns a source-linked trace. We evaluated system-level classification
against three baselines (NHANES, which also informed rule development; KNHANES), rule-level direction under a pre-registered
three-state standard (CHARLS; eight cohorts, 285,878 participants), and
concordance across four literature indexes. We audited which pairs the rule revision had
touched, repeated the external comparison without them, and asked the agent
whether each of 18 cohort cells would replicate.

**Results.** The internal matrix had no replicated pair untouched by the revision
(0 of 6), so it yields no out-of-sample estimate (agent 0.571 versus rule
layer 0.522; development only). Externally, on 301 KNHANES pairs it scored 0.375
against 0.360 for its own rule layer and 0.176, 0.173, 0.120 for LightRAG, a pure
LLM and naive RAG. On the 296 untouched pairs the ordering held
but levels collapsed to 0.211, 0.200, 0.122, 0.089 and 0.086; the agent's gain is
precision, not recall (recall 0.500 either way). On 18 cohort cells, assuming transport
gave 0.615, the evidence gate flagged none, and a plain LLM reached 0.667 but
endorsed 1 of 2 contradicted cells. Rule track: 6 of 21 rules were
cohort-testable; of 18 rule x cohort pairs 8 replicated, 8 were uninformative and
2 contradicted; two met the pre-registered criterion but both intervals spanned
unity. Literature concordance: 0.889 (PubMed), 0.916 (Web of Science), 0.922 (Europe
PMC), 0.800 (CNKI); 16/17 index agreement.

**Conclusions.** The agent beat LLM and RAG baselines, and narrowly its rule layer,
externally; only a fifth of that F1 survives removing the pairs
that informed development, and its evidence machinery does not transfer to
population-level questions. Its rules were largely untestable elsewhere (15 of 21) and none was robustly
transportable where testable; the constraint was measurement, not sample size. Agent validation should report system- and rule-level
results separately, disclose which pairs informed development, and
state which exposures were measured.
