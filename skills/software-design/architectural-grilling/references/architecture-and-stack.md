# Grounded Architecture and Tech Stack

Use this guide when the interview must choose or challenge architecture, frameworks, infrastructure, or a tech stack. Apply it through the existing one-question loop. The goal is a justified recommendation the user can accept, not a separate questionnaire, scoring ritual, or mandatory stack template.

## Establish the decision horizon

Use discovered facts and prior answers first. Resolve only unknowns that could change the recommendation:

- the next useful release or learning milestone, its deadline, and the cost of delay;
- current demand, evidence-backed demand within that horizon, and aspirations outside it;
- workload shape: concurrent activity, request or job rate, payloads, data volume, bursts, long-running work, and relevant latency or recovery targets;
- the people who build and operate it, their existing expertise, available maintenance time, budget, and support responsibilities;
- hard obligations, integrations, existing assets, and costly or irreversible decisions.

Treat user count as context, not a capacity model. A forecast is not a benchmark; a signed launch commitment can justify preparation before traffic exists. When capacity is unknown and material, propose a bounded representative measurement with a decision rule instead of inventing a limit. Do not require that measurement to settle unrelated branches.

## Make complexity earn its place

Start with the simplest credible solution in this environment: extend an existing system, use a managed product, or keep one deployable application with clear internal boundaries when appropriate. Compare it with the strongest realistic alternative. Evaluate total delivery and operating effort, not just the number of services or the hosting bill.

For each consequential addition, establish:

1. **Need:** the present problem or credible commitment it addresses and the evidence behind it.
2. **Alternative:** why the simpler option is insufficient, including any inexpensive change that might make it sufficient.
3. **Burden:** setup, integration, deployment, monitoring, upgrades, debugging, incidents, recovery, money, and the named person or team who can absorb them.
4. **Timing:** the cost of introducing it now versus later, reversibility, migration lead time, and what is lost by waiting.

Independent deployments, measured resource contention, failure isolation, contractual requirements, or clear ownership boundaries can justify additional components. A component should not survive merely because it is fashionable, might be useful someday, or already appears in an architecture diagram.

Assess marginal burden in context. An established platform with a capable owner may cost less to retain than to replace with a nominally simpler service. Managed offerings shift work rather than eliminate cost, limits, or vendor dependency. Do not turn team size or a technology name into a universal prohibition.

If the user explicitly values learning, portability, or another preference and accepts its cost, record that conscious trade-off. Challenge its consequences once; do not relabel it as a production requirement or keep arguing after it is resolved.

## Turn architecture into a concrete stack

Once the drivers are sufficient, recommend technologies rather than asking the user to choose from an unexplained catalog. Preserve delegated decision rights and mark proposals as unconfirmed until accepted under the main operating contract.

1. Map the smallest end-to-end journey to responsibilities: interface, application/domain behavior, source of truth, necessary integrations, and deployment. Clarify which responsibilities share a process, deployment, or datastore. A module is not automatically a service.
2. Fill only needed roles with named technology candidates: language/runtime, UI, application framework, persistence, access control, hosting, and essential verification/operations. Add jobs, cache, search, messaging, object storage, or other specialized services only when the journey or an obligation requires them. For an existing product, focus on choices that actually need changing.
3. Check that the choices fit together: runtime/hosting compatibility, data access, deployment model, authentication boundaries, supported integrations, and the team's ability to debug the whole path. Do not assemble independently fashionable winners into an incoherent stack.
4. Favor team competence and maintained existing assets when they meet the requirements. Compare realistic learning, hiring, integration, testing, maintenance, licensing, support, lock-in, and migration costs when proposing a change. An existing tool is a useful default, not an obligation to retain an unsuitable one.
5. State the strongest credible alternative, why it loses here, and the accepted drawback of the recommendation. Use qualitative trade-offs unless actual measurements justify numbers; avoid arbitrary weighted scores or fixed rankings.

Recommend a direction as soon as the evidence supports it, then refine only decisions affected by new answers. Do not withhold all guidance until the final blueprint. If a missing fact could change the choice, name the provisional choice and its validation condition, and ask only the next blocking question.

Check current primary documentation for material version support, compatibility, pricing, quotas, licensing, and product capabilities. If verification is unavailable, label the claim unverified and retain an evidence gate with an owner and decision rule. Do not promise a cost or capacity based on a remembered vendor table. The final blueprint can name a technology family or product conditionally without pretending an exact version or provider has been validated.

## Separate preparation from premature construction

Classify consequential choices, without forcing a separate artifact:

| Disposition | What it means |
| --- | --- |
| Build now | Required by the agreed release, a hard obligation, or a credible risk whose delay cost warrants action. Include its owner and acceptance evidence. |
| Prepare cheaply | A concrete low-cost measure that preserves an option: a clear module boundary, portable data export, basic workload telemetry, or a tested restore path. Explain the benefit and present cost. |
| Defer until a trigger | Keep a safe baseline and record the owner, observable signal or dated evidence check, response, migration lead time, and accepted risk. |

Do not disguise future construction as preparation: unused adapters, general-purpose extension frameworks, dormant services, speculative schemas, or parallel deployment paths still require maintenance. A plausible migration outline is usually enough; an expensive-to-reverse data boundary may deserve a present decision. Calibrate each to the consequences of waiting.

Choose triggers tied to the limiting requirement: a latency objective missed under representative load after reasonable tuning, recovery needs the current design cannot satisfy, independent release ownership, or a verified cost crossover. Define the threshold or evidence check with the user; do not invent universal user/service counts. Allow enough warning and lead time to act before a commitment fails. "Revisit when we grow" is not a decision rule.

Do not defer required authorization, data integrity, backups, recovery, or other applicable safeguards just because the first release is small. Conversely, a remote hypothetical feature with no present consequence can remain an explicit non-goal without spawning a migration project.

## Example of interview pressure

For a small internal product with a distant ambition of 10,000 users, challenge whether the proposed distribution solves a current workload or ownership problem. Recommend a concrete candidate using the team's known tools, explain the operating cost it avoids, and propose a relevant revisit signal. Then ask one decision, for example: "Do you accept a single deployable application for this release, with service extraction reconsidered if measured contention prevents meeting the agreed latency target?"

Do not use that answer automatically when a committed launch, isolation obligation, or existing staffed platform changes the evidence.

## Source basis

The following primary skills were reviewed on 2026-09-02. The guidance above is an adaptation of their decision criteria to this skill's interview contract; these links are attribution, not runtime dependencies:

- [architecture-pattern-selector](https://github.com/alirezarezvani/claude-cto-team/blob/main/skills/architecture-pattern-selector/SKILL.md): pattern selection from workload, team and operational constraints; alternatives, trade-offs, confidence, and evolution triggers.
- [architecture-designer](https://github.com/jeffallan/claude-skills/blob/main/skills/architecture-designer/SKILL.md): functional and quality requirements, boundaries, failure modes, operational consequences, and reasoned architecture decisions.
- [tech-stack-recommender](https://github.com/alirezarezvani/claude-cto-team/blob/main/skills/tech-stack-recommender/SKILL.md): technology fit with team expertise, project needs, ecosystem, delivery budget, support, and migration cost.

Do not import their numeric cutoffs, fixed weighting formulas, frozen technology/version tables, or full review processes as universal rules. No installation of these skills is required.
