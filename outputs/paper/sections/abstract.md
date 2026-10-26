# Abstract

**Background.** Clinical decision support for major eye disease increasingly uses
multi-layer agents that combine deterministic rules, knowledge-graph retrieval and
a language model. Such agents are inspectable, but whether they outperform
general models on common data, and whether their rules hold elsewhere,
are rarely tested together.

**Methods.** We built Huiyan, an explainable agent combining 21 rules, a LightRAG
knowledge graph of 1,060 evidence chunks and an LLM arbiter that grades
risk and returns a source-linked trace. We evaluated two validation tracks across
four independence tiers: system-level classification of the deployable agent
against three baselines (internal NHANES; external KNHANES), and rule-level
direction under a pre-registered three-state standard (CHARLS; eight ageing cohorts,
285,878 participants), plus
independent concordance across four literature indexes.

**Results.** System track: the deployable agent ranked first on F1 in every
matrix — 0.571 on NHANES (80 pairs; LightRAG 0.392, pure LLM 0.335, naive RAG
0.080) and 0.480 on the GLM generation (159 pairs; 0.186, 0.178, 0.069);
on KNHANES (301 pairs) the rule layer scored 0.360 versus 0.145, 0.135 and 0.094.
Under a binary collapse the agent reached sensitivity 1.00, specificity 0.878,
PPV 0.400 and κ 0.520 internally; external sensitivity fell to 0.50. Rule track:
only 6 of 21 rules were testable in the cohorts; of 18 rule × cohort pairs, 8
replicated, 8 were uninformative and 2 contradicted; two met the pre-registered
criterion, but both prediction intervals spanned unity. Literature concordance
was 0.889 (PubMed, 21 informative rules), 0.916 (Web of Science, 2), 0.922
(Europe PMC, 17) and 0.800 (CNKI, 5), with 16/17 PubMed–Europe PMC
cross-index agreement. Every reported case resolved to a rule, a KG path
and a source chunk (Multimedia Appendix 1).

**Conclusions.** An explainable rule-KG-LLM agent can be benchmark-validated and
operable: it ranked first against LLM and RAG baselines across two national
surveys and returns a source-linked report through a working interface. Its
rules, however, were largely untestable elsewhere (15 of 21), and none was
robustly transportable where testable; the constraint was measurement, not
sample size. Agent validation should therefore report system-level and rule-level
results separately, and state which exposures were measured.
