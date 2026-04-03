# Device Concept — OBE Induction System

*A working document. The goal is to design a device or integrated system that reliably facilitates OBE induction — an updated Gateway, but more than audio, and adaptive.*

---

## The Core Problem with Existing Tools

The Monroe Institute's Gateway Tapes are the most serious attempt to date at systematic OBE induction. Their limitation is structural: the stimulus is fixed, the user is variable. The tape plays identically whether you're scattered or already at threshold. There is no feedback loop. The device doesn't know where you are.

Every other consumer tool — light/sound machines, lucid dreaming masks, binaural beat apps — inherits this same problem. They apply a predetermined stimulus and hope it lands.

A genuinely effective system has to close the loop. It listens as it speaks.

---

## Design Principles

**1. Adaptive, not fixed.**
The system continuously reads the user's physiological state and adjusts stimulus in real time. When you're close, it shifts to a maintenance protocol. When you've drifted, it intensifies induction.

**2. Multi-modal.**
No single stimulus channel is sufficient. The system combines audio, visual, haptic, and potentially electromagnetic inputs — each targeting a different aspect of the threshold transition.

**3. Personalized over time.**
Each user has a unique threshold signature — the biometric pattern that appears consistently in the minutes before the vibrational state. The system builds a model of this signature through repeated sessions and optimizes accordingly.

**4. Non-invasive.**
Consumer EEG, haptic vibration, photic stimulation. No implants, no clinical equipment. The system should be usable at home, alone, in ordinary conditions.

**5. Grounded in phenomenology.**
The design is informed by someone who has actually reached threshold. Jacob's field notes are the ground truth the system is calibrated against.

---

## Stimulus Modalities

### Audio — Binaural Beats & Spatial Sound
The foundation, inherited from Monroe. Binaural beats work by presenting slightly different frequencies to each ear, inducing an auditory processing effect that entrains brainwave activity toward target states.

**Target frequencies:**
- *Alpha (8–12Hz)* — Initial relaxation, body settling
- *Theta (4–7Hz)* — The hypnagogic zone. Where the vibrational state appears. The primary target.
- *Delta (0.5–4Hz)* — Deeper dissociation. Post-vibrational, approaching separation.

**Beyond binaural beats:** Spatial audio — sounds that move through 3D space — may help dissolve the body's sense of fixed location. The sense of self-as-point-in-space is one of the things that has to relax for separation to occur. Audio that doesn't behave the way a fixed-position body would expect may help loosen that anchor.

**Adaptive layer:** The audio engine receives EEG input and adjusts frequency targets in real time. If theta is rising, the system holds steady. If it drops, the binaural frequency intensifies.

---

### Haptic — Physical Vibration
The most underexplored modality, and potentially the most direct.

The vibrational state is the body's signal that something is changing. External vibration at the right frequency — delivered through a mat, vest, or wristband — may prime or amplify the internal sensation. The hypothesis is resonance: a physical vibration that matches the felt quality of the inner vibrational state creates a bridge between the external stimulus and the internal response.

**Candidate frequencies:** Low-frequency vibration in the 7–12Hz range (corresponding to alpha/theta). Infrasound (below 20Hz) has documented effects on spatial perception and the sense of presence — relevant given the "presence" phenomenon documented in `phenomena.md`.

**Adaptive layer:** Haptic intensity modulated alongside audio based on EEG state. As theta rises, haptic may reduce (so as not to compete with the emerging internal state) or shift frequency to support stabilization.

---

### Visual — Photic Stimulation
Light flicker at specific frequencies entrains the visual cortex and can deepen trance. This is established technology (AudioStrobe, the Laxman device) but has never been integrated with a biofeedback loop in a consumer product.

**Target:** Theta-range flicker (4–7Hz) during induction, shifting to slower flicker or darkness as the hypnagogic threshold approaches. The appearance of threshold light phenomena (the purple light) may itself be a signal to shift protocol — from induction to maintenance.

**The threshold light question:** When Jacob's purple light appears, the system should recognize this as a depth marker and adjust — not continue pushing induction, but hold the state and allow it to develop.

**Adaptive layer:** The photic stimulus is the most sensitive to timing. Too much visual stimulation too late in the induction disrupts the transition. EEG-guided cutoff: when theta is stable and theta power peaks, photic stimulation fades out.

---

### Electromagnetic — Temporal-Parietal Stimulation
The most speculative modality, but grounded in real neuroscience.

The temporal-parietal junction (TPJ) is the brain region most consistently implicated in OBE phenomenology. Neuroimaging studies of spontaneous OBEs, and of seizure-induced OBEs, consistently point to the TPJ as the site where the brain constructs its model of body ownership and self-location. Disruption of TPJ function — through stroke, epilepsy, or laboratory stimulation — produces OBE-like experiences.

Michael Persinger's "God Helmet" applied weak, complex magnetic fields to the temporal lobes. The replication record is contested. But the underlying anatomy is not: the TPJ is the right target.

A non-invasive, consumer-safe magnetic stimulation device targeting the TPJ — timed to coincide with the deepest theta state in the session — is a legitimate avenue to explore. This is the most technically demanding component and probably the last to develop.

---

## The Biofeedback Architecture

```
Sensors → Signal Processing → State Classifier → Stimulus Engine
   ↑                                                      ↓
   └──────────────── Feedback Loop ──────────────────────┘
```

**Sensors:**
- EEG headband (consumer: Muse 2, OpenBCI Cyton for research-grade)
- Heart rate / HRV (chest strap or wristband)
- Galvanic skin response (optional — useful for arousal detection)
- Respiration rate

**State Classifier:**
Maps sensor data to induction states:
- *Pre-threshold* — Body relaxed, mind drifting. Intensify induction.
- *Approaching threshold* — Theta rising, HRV settling. Hold current stimulus.
- *At threshold* — Theta peak, possible vibrational state onset. Shift to maintenance protocol.
- *Vibrational state active* — Characteristic EEG pattern (to be established from Jacob's sessions). Reduce all external stimulus. Allow the internal state to develop.
- *Drifted / asleep* — Delta dominant, no awareness markers. Gentle theta reinduction or session end.

**Stimulus Engine:**
Receives state classifications and outputs coordinated instructions to audio, haptic, photic, and (eventually) electromagnetic systems.

---

## Personalization Layer

Over repeated sessions, the system builds a user profile:

- What is this user's typical theta onset time?
- What biometric pattern precedes their vibrational state?
- What stimulus intensity causes collapse versus stabilization?
- What time of day produces deepest sessions?

This is the AI component. Not a language model but a pattern-recognition system that learns the individual's threshold signatures and adjusts the induction protocol accordingly.

Jacob's advantage: he has already reached the threshold multiple times. The first calibration sessions are not starting from zero — they are documenting a known territory.

---

## Prototype Roadmap

**Phase 1 — Baseline Mapping** *(Now)*
Wear a consumer EEG headband (Muse 2) during Gateway sessions. Record sessions with timestamps. Correlate EEG data with field notes. Goal: identify the biometric signature of Jacob's threshold states.

**Phase 2 — Adaptive Audio**
Build a simple adaptive binaural beat system. Input: EEG data. Output: real-time frequency adjustment. Test against fixed-stimulus baseline. This is achievable with existing consumer hardware and open-source EEG toolkits.

**Phase 3 — Haptic Integration**
Add a haptic layer. Vibration mat or vest. Calibrate frequency and timing against Phase 2 data. Test resonance hypothesis.

**Phase 4 — Photic Integration**
Add photic stimulation. Calibrate cutoff timing. Build threshold-light detection logic (if possible from EEG signature).

**Phase 5 — Full System + Personalization**
Integrate all modalities. Begin building personalization model from accumulated session data. Refine.

**Phase 6 — TPJ Stimulation** *(Speculative)*
If Phases 1–5 produce reliable threshold induction, add electromagnetic component. Requires more technical development and careful safety research.

---

## Research Threads to Follow

- OpenBCI documentation and community (research-grade EEG, open-source)
- Muse 2 developer SDK (consumer EEG, accessible starting point)
- Infrasound and presence effects: Vic Tandy's work; Persinger's environmental studies
- TPJ and OBE neuroscience: Blanke et al., Ehrsson et al.
- Hypnagogia and EEG: Hori et al. sleep onset stage research
- Monroe Institute research archive

---

## Connection to the Consciousness Map

The device and the map are the same project from different angles.

The map is cartography — what is the territory? The device is the vehicle — how do you get there reliably? Every session with the device generates field notes that enrich the map. Every landmark on the map informs what the device should be targeting.

Jacob's direct experience is the ground truth both depend on. The biometric signatures the device learns to recognize are the physiological correlates of the phenomenological landmarks documented in `phenomena.md`.

---

*Document initiated April 2026. To be developed as the project progresses.*
