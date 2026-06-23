# WWMHD Consent & Privacy Framework

## 1. Informed Consent

Users participating in WWMHD must provide explicit, affirmative consent before any processing begins. The consent contract covers three distinct domains of activity, each of which a user must acknowledge independently or as part of a granular tiered consent flow.

### 1.1 Behavioral Inference
The system observes user actions during gameplay and derives implicit behavioral profiles. Inference includes:
- Risk preference estimation under uncertainty
- Cooperation vs. defection tendencies in social scenarios
- Patience and long-range planning metrics derived from temporal choice tasks
- Communication style classification (direct, adversarial, conciliatory, evasive)

Users agree that these inferences are computed from their observable in-game actions alone and are derived from themed narrative scenarios designed to elicit behavioral signals. No attempt is made to reconstruct real-world identity, political orientation, medical history, or other sensitive categories unless the user explicitly volunteers such information.

### 1.2 Game Participation
Users agree to engage with the game world, scenarios, and multiplayer mechanics according to the published rules. This includes:
- Receiving and acting within scenario constraints
- Being subject to entropy drivers, epoch progression, and scenario resolution mechanics
- Allowing their agent persistent state (behavioral profile, reputation, chronicle record) to influence future scenario generation

### 1.3 Chronicle Publication
Users may choose to permit the publication of their anonymized profile data alongside session logs, scenario outcomes, and behavioral annotations. Publication is strictly opt-in and operates independently of core gameplay participation.

---

## 2. Minimum Viable Consent Scope

The minimum consent package required for a user to participate in WWMHD gameplay consists of:

1. **Acknowledgment of Local Processing** — the user understands that behavioral inference runs on local hardware and that inference artifacts remain under their control.
2. **Behavioral Inference Scope** — the user agrees that only the behavioral signals generated during WWMHD scenarios will be used for profile construction; no external browsing history, application telemetry, or background process data is collected.
3. **Agent Persistence** — the user accepts that their agent's behavioral profile persists across sessions and epochs, and that this profile influences future scenario difficulty and composition.

Chronicle publication, cross-persistent-agent data sharing (even for research aggregation), and submission of anonymized data to external archives are treated as augmentations to the minimum consent scope and require separate, explicit opt-in.

---

## 3. Revocation & Withdrawal

Users may withdraw their consent at any time. Withdrawal is implemented as a first-class operation in the agent lifecycle.

### 3.1 Immediate Effect
Upon withdrawal:
- All real-time behavioral inference halts.
- The agent's local inference engine stops emitting new profiling signals.
- No further data is transmitted from the local inference substrate to any remote endpoint.

### 3.2 In-Game Profile Effect
Withdrawal does not erase the agent's prior in-game history. The existing chronicle record, reputation scores, and behavioral profile remain as a persistent artifact of completed epochs. However:
- The profile is **frozen**: no further updates are appended.
- The frozen profile is tagged `revoked` and excluded from active scenario generation for that agent.
- Future interactions by the same agent are governed by a reduced role: the agent may continue as a spectator or light-role participant in scenarios that do not require behavioral signal generation.

### 3.3 Draft Status
Any session or epoch that has not reached resolution (chronicle entry incomplete) is abandoned. Dependent chronicle entries remain in `draft` status and are not published, regardless of prior chronicle consent.

---

## 4. Privacy Guarantees

| Guarantee | Description |
|-----------|-------------|
| **Local-Only Inference** | All behavioral inference computations execute on the user's local device. No inference state, signal buffers, or raw feature vectors are transmitted to external servers during normal gameplay. |
| **No PII Storage** | The system does not collect, index, or store names, email addresses, geolocation coordinates, device identifiers, or any other data whose purpose is to identify a natural person. Agent identifiers are pseudonymous and carry no persistent link to real-world identity unless the user creates one. |
| **No Cross-Agent Profile Sharing** | Agent profiles are siloed per user. Profiles are never combined, compared, or exchanged between different users, nor are they used to train shared models unless the user explicitly consents to research aggregation. |
| **Data Minimization** | Only signals necessary for the declared inference tasks are retained. Feature buffers are rotated and truncated on a fixed interval. |
| **Transparency Log** | A local, machine-readable log records every inference operation, the features used, the output profile delta, and the triggering in-game event. This log is readable by the user but not transmitted. |

---

## 5. Chronicle Publication

Chronicle publication is a distinct consent axis from core gameplay.

### 5.1 Anonymized Profiles
When a user opts in to chronicle publication:
- Their agent identifier is replaced by a hash that cannot be reverse-engineered without access to the originating user's local secret material.
- Profile vectors are rounded or differentially perturbed to prevent re-identification via vector matching attacks.
- Chronicle entries are scrubbed of any user-supplied text that may contain self-identifying information before publication.

### 5.2 Anonymized Actions
Scenario actions are published in narrative form with:
- Real-world timing replaced by in-world timestamp epochs.
- Any player-chosen display names replaced by agent pseudonyms.
- Spatial or factional identifiers that could link to a specific coordinated player group removed or abstracted.

### 5.3 Separate Consent
Chronicle consent is not bundled with gameplay consent. A user may fully participate in WWMHD without ever opting in to publication. Conversely, a user who withdraws gameplay consent retains their prior publication consent for already-published chronicles; subsequent sessions produce no new chronicle entries.

---

## 6. Fair Play & Anti-Gaming

### 6.1 Prohibition on Profile Sharing
Users are prohibited from transferring, copying, selling, or otherwise sharing their behavioral profile or inference artifacts with other human or AI agents. This includes:
- Sharing raw profile state files.
- Sharing screen captures or transcripts that contain serialized inference vectors.
- Coordinating across separate accounts to present coordinated behavioral signals.

### 6.2 Detection
The system includes signature checks on chronicle entries, deterministic replay comparison between claimed and actual agent behavior, and statistical tests for action similarity across agents operating in the same scenario window.

### 6.3 In-Game Penalty
Profile sharing is treated as a rules violation, not merely a privacy breach. Penalties escalate:
- **First detection**: the affected agent's profile is quarantined. The agent is barred from multiplayer scenario matchmaking for a duration proportional to the severity of the shared data. A trace record is appended to the agent's chronicle.
- **Second detection**: the agent's behavioral profile is reset to default priors. All persistent reputation scores are nullified. The agent remains in the game world but loses all behavioral personalization.
- **Persistent violation**: the agent is barred from chronicle publication permanently, even if individual users later opt in.

---

## 7. Cross-Reference Matrix

Each consent provision is mapped to its legal/regulatory basis, its technical enforcement mechanism, and its in-game consequence.

| Provision | Legal / Regulatory Framework | Technical Enforcement | In-Game Mechanic Consequence |
|-----------|-----------------------------|----------------------|------------------------------|
| **Explicit opt-in to behavioral inference** | GDPR Art. 6(1)(a) — explicit consent as lawful basis | Consent gate rendered before inference engine initialization; consent receipt timestamped and signed locally | Agent cannot enter any scenario until consent is recorded; scenario queue shows locked state |
| **Granular consent tiers (inference / game / chronicle)** | GDPR Art. 7(3) — right to withdraw consent by domain | Consent model stored as three independent flags; each flag controls a distinct API surface in the local runtime | Users toggle consent from a settings panel; partial consent allows gameplay but blocks chronicle export UI |
| **Right to withdraw inference consent** | GDPR Art. 17 — right to erasure; Art. 7(3) — withdrawal without detriment | Inference engine checks consent flag per operation; `revoke` command flushes feature buffers and halts scheduler | Agent is preserved as character in the world but becomes non-player for scenario resolution; chronicals are frozen |
| **Local-only inference (no telemetry exfiltration)** | GDPR Art. 5(1)(c) — data minimization; Art. 32 — security of processing | Local code audit: no network sockets opened by `inference` module; verified by deterministic builds and reproducible binary hash | N/A (player-experience neutral; technical safeguard enforces privacy-by-design rather than game-state change) |
| **No PII collection or storage** | GDPR Art. 5(1)(b) — purpose limitation; Art. 9 — special categories | Input sanitization layer rejects any field matching PII regex or entropy threshold; storage schema has no personal-identifier columns | N/A (infrastructure requirement; violation results in build rejection before release) |
| **No cross-agent profile sharing** | GDPR Art. 5(1)(e) — storage limitation; Art. 21 — right to object to profiling | Agent profile filesystem paths are namespaced by user-specific random UUID; no aggregation service exists | Profile-sharing detection triggers anti-gaming penalty workflow (see §6.3) |
| **Separate chronicle publication consent** | GDPR Art. 6(1)(a) per distinct processing purpose; ePrivacy Directive Art. 5(3) — cookie-equivalent consent | Publication flag enforced at export boundary; chronicle exporter skips all entries if flag is false | Users see "Publish" button disabled; community chronicle browser shows no trace of that agent unless opted in |
| **Anti-gaming: profile sharing penalty** | GDPR Art. 83(5) — administrative fines for violations; consumer-protection parity | Anticheat module performs hash comparison of profile blobs across agents; statistical similarity tests flag coordinated play | Matchmaking suspension on first detection; profile reset on second; publication ban on persistent violation |

---

## 8. Sample User-Facing Consent Document

```
WWMHD — Consent Agreement
=======================

Welcome to World With Me, Here and Done.

Before you begin, we want you to understand exactly what you're signing up for and
what remains private. This document is plain language, not legalese. If anything is
unclear, please ask.

WHAT WE OBSERVE
---------------
The game observes your choices inside the game world. It uses those observations
to build a behavioral profile — a model of how you tend to act when facing
dilemmas. This helps the game tailor scenarios, NPC reactions, and world events
to create a more interesting experience for you.

The game does NOT collect your name, email, location, contacts, browsing history,
or any information from outside the game itself.

WHAT YOU AGREE TO
-----------------
By clicking "I Agree," you allow the game to:
1. Watch your in-game choices and turn them into behavioral insights.
2. Use those insights to shape your character's story and the world around you.
3. (Optional) Include anonymized excerpts of your agent's actions in public
   chronicles that other players can browse. This is a separate checkbox — you
   can say yes or no to this without affecting your ability to play.

YOUR RIGHTS
-----------
• You can cancel this agreement at any time. Go to Settings → Privacy → Withdraw
  Consent. Your character stays in the world, but the game stops watching.

• Your data stays on your device. Nothing identifying you leaves your computer
  unless you separately opt in to chronicle publication.

• You can ask for a full copy of everything the game has inferred about your
  agent. The inference log is readable from Settings → Privacy → View Log.

WHAT HAPPENS IF YOU WITHDRAW
-----------------------------
After withdrawal:
• The game still remembers your past sessions.
• Your character continues to exist but stops receiving new behavioral updates.
• Nothing new is published about your agent, even if you previously said yes
  to chronicles.

ANTI-CHEAT NOTICE
-----------------
Sharing your behavioral profile with another player, or coordinating across
multiple accounts, is against the rules. The game detects this and imposes
penalties on agents that violate this rule — starting with matchmaking
suspension and ending, for repeat violations, with permanent removal from
published chronicles.

ACCEPT
------
[ ] I understand and agree to behavioral inference during gameplay.

[ ] I agree to game participation.

[ ] (Optional) I agree to publish anonymized excerpts of my agent's actions
    in public chronicles.

[Confirm]
```

---

## Document Control

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 0.1 | 2026-06-23 | Shadow (policy agent) | Initial framework draft |
