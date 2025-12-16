# Simulating Habermas’s Ideal Speech Situation: Does Rational Consensus Emerge in Constrained Multi-Agent LLM Debates?

This paper asseses whether Large Language Models (LLMs) adhere to Jürgen Habermas's Ideal Speech Situation principles during unconstrained debates, and whether explicitly constraining LLMs with ideal speech rules affects consensus formation and epistemic quality.

## Files Descriptions

## Experiment Design
This research employed 3 experimental setups to examine ideal speech principle adherence and consensus formation in LLM debates. All three setups used the same 10 debate topics to enable direct comparison, with debates reaching similar overall lengths across conditions despite different structural constraints.

### Setup 1: Argum.ai structured debates
Argum (Argum.ai 2024) is a platform that facilitates structured debates between AI agents. Users select debate topics and models, and the framework evaluates debates to reach verdicts. Ten publicly published debates were randomly selected from this platform:
- Is teamwork or solo work better?
- Is exercise or diet an easier way to lose weight?
- Is it better to limit social media use versus accepting it as integral to modern life?
- Should you save for the future or enjoy your money while you can?
- Is it better to delegate tasks or do it yourself to ensure quality?
- Would you rather have a stable job or a risky business with high returns?
- Should you pay off debt first or start investing early?
- Financial freedom: Focusing on passive income versus active investments
- Does social media inspire more than it fosters competition?
- You get a promotion that doubles your pay but triples your stress. Take the money or protect your sanity?
Each debate here consisted of exactly 6 turns following a rigid format- 2 opening statements, 2 rebuttals, and 2 closing statements, with agents alternating turns. We do not have access to the system prompts used to initialize agents, so we cannot determine whether ideal speech principles were explicitly encoded. However, the structured format itself imposes procedural constraints on argumentation. Argum provided a baseline dataset to analyze whether ideal speech constraints were being followed by out-of-the-box LLMs and whether consensus was being reached.

### Setup 2: Unconstrained Free-Flowing Debate
To test whether ideal speech principles emerge naturally without explicit enforcement, unconstrained debates were conducted using the same 10 topics with three LLM agents (llama-3.3-70b-versatile).
Unlike Argum’s fixed structure, this setup implemented free-flowing debate consistent with Habermas’s principle of equal participation rights. After each statement, agents independently decided whether to speak and rated their confidence in this decision (0.0-1.0). Confidence ratings served two purposes:
- They provided a measure of agents’ certainty about their participation choices, allowing analysis of whether agents exhibited the overconfidence patterns documented in previous LLM debate research (Prasad and Nguyen 2025)
- They operationalized Habermas’s accountability principle by requiring agents to explicitly represent their level of conviction when choosing to speak or remain silent.
All agents made opening statements to initiate debate. Subsequently, agents could speak when they chose, but could not speak consecutively: an agent who had just spoken was required to pass their next turn. This constraint prevented domination while preserving voluntary participation.
Debates ended when 30 turns were reached, 5 minutes elapsed or all agents consecutively passed, indicating no further substantive contributions (an end had to be imposed due to computational resource constraints).

### Setup 3: Ideal Speech-Constrained Debate
The third setup maintained the free-flowing structure but explicitly encoded Habermas's discourse principles in agent initialization. Agents were instructed to explicitly follow ideal speech rules:
1. **Truthfulness**: Make only claims you believe to be true and can support with reasoning
2. **Sincerity**: Express your genuine understanding and beliefs
3. **Rationality**: Provide logical arguments and valid reasoning
4. **Comprehensibility**: Express ideas clearly and accessibly
5. **Respect**: Acknowledge others' arguments fairly before responding
6. **Good Faith**: Aim to reach mutual understanding, not just "win"
7. **No Fallacies**: Avoid ad hominem, strawman, and other logical fallacies
8. **Evidence-Based**: Support claims with reasoning or evidence when possible

## Analysis Methods


## Results
