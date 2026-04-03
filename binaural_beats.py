#!/usr/bin/env python3
"""
Binaural Beats — Consciousness State Navigator
================================================
A tool for the Consciousness Map project.

Generates real-time binaural beats mapped to brainwave states and
Monroe Institute focus levels. Designed for use with stereo headphones.

Requirements:
    pip install numpy sounddevice

Usage:
    python binaural_beats.py

Author: Jacob Cantrell & Claude — Consciousness Map Project, April 2026
"""

import numpy as np
import threading
import time
import sys
import os
import signal

try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except (ImportError, OSError):
    sd = None
    AUDIO_AVAILABLE = False

# ─────────────────────────────────────────────────────────────
# CONSCIOUSNESS STATE DEFINITIONS
# ─────────────────────────────────────────────────────────────

BRAINWAVE_BANDS = {
    "delta": {
        "range": (0.5, 3.99),
        "description": "Deep sleep, unconscious processes, healing",
        "color": "\033[35m",  # magenta
    },
    "theta": {
        "range": (4.0, 8.0),
        "description": "Hypnagogic zone, deep meditation, vibrational state territory",
        "color": "\033[34m",  # blue
    },
    "alpha": {
        "range": (8.0, 13.0),
        "description": "Relaxed awareness, body settling, light meditation",
        "color": "\033[36m",  # cyan
    },
    "beta": {
        "range": (13.0, 30.0),
        "description": "Active thinking, focused attention, problem-solving",
        "color": "\033[33m",  # yellow
    },
    "gamma": {
        "range": (30.0, 44.0),
        "description": "Peak cognition, insight, heightened perception, unity states",
        "color": "\033[37m",  # white
    },
}

# Monroe Focus Levels mapped to binaural beat frequencies and carrier tones.
# These are informed by the Gateway Experience framework and the research
# documented in the Consciousness Map project.
FOCUS_LEVELS = {
    "focus_10": {
        "name": "Focus 10 — Mind Awake / Body Asleep",
        "beat_freq": 10.0,       # Alpha — body settling into sleep
        "carrier_freq": 200.0,   # Base carrier tone
        "band": "alpha",
        "description": (
            "The body enters sleep while conscious awareness remains.\n"
            "  This is the threshold state where the vibrational state\n"
            "  often first appears. The gateway to everything beyond."
        ),
        "duration_default": 20,  # minutes
    },
    "focus_12": {
        "name": "Focus 12 — Expanded Awareness",
        "beat_freq": 6.0,        # Theta — deeper, expanded perception
        "carrier_freq": 196.0,
        "band": "theta",
        "description": (
            "Sensory noise drops. Perception extends beyond the physical\n"
            "  body's immediate environment. A state of receptivity.\n"
            "  Theta-frequency binaural beats facilitate deep meditation."
        ),
        "duration_default": 25,
    },
    "focus_15": {
        "name": "Focus 15 — No Time",
        "beat_freq": 4.5,        # Low theta — temporal dissolution
        "carrier_freq": 185.0,
        "band": "theta",
        "description": (
            "Ordinary temporal sequencing dissolves. Past and future\n"
            "  become accessible as fields rather than sequences.\n"
            "  The void. Pure potential."
        ),
        "duration_default": 30,
    },
    "focus_21": {
        "name": "Focus 21 — The Bridge",
        "beat_freq": 2.5,        # Delta-theta border — edge of physical
        "carrier_freq": 175.0,
        "band": "delta",
        "description": (
            "The edge of the physical matter energy system. The threshold\n"
            "  where contact with non-physical realities becomes possible.\n"
            "  Monroe described this as the bridge state."
        ),
        "duration_default": 35,
    },
    "focus_27": {
        "name": "Focus 27 — The Park",
        "beat_freq": 1.5,        # Deep delta — far from physical
        "carrier_freq": 165.0,
        "band": "delta",
        "description": (
            "The edge of human thought capacity. Monroe's Reception Center.\n"
            "  Deep delta territory. The furthest mapped landmark in the\n"
            "  Gateway framework."
        ),
        "duration_default": 40,
    },
}

# Session presets — multi-phase protocols that transition between states
SESSION_PRESETS = {
    "gateway_induction": {
        "name": "Gateway-Style Induction",
        "description": (
            "A progressive deepening from waking to Focus 12.\n"
            "  Mirrors the Gateway Experience approach: settle the body,\n"
            "  then expand awareness."
        ),
        "phases": [
            {"label": "Settling (Alpha)",     "beat": 10.0, "carrier": 200.0, "minutes": 5},
            {"label": "Deepening (Theta)",    "beat": 7.0,  "carrier": 196.0, "minutes": 5},
            {"label": "Focus 10 Hold",        "beat": 10.0, "carrier": 200.0, "minutes": 8},
            {"label": "Focus 12 Transition",  "beat": 6.0,  "carrier": 196.0, "minutes": 10},
            {"label": "Return (Alpha)",       "beat": 10.0, "carrier": 200.0, "minutes": 3},
        ],
    },
    "theta_hold": {
        "name": "Deep Theta Hold",
        "description": (
            "For vibrational state practice. Quickly settles into theta\n"
            "  and holds there — the hypnagogic zone where the vibrational\n"
            "  state appears."
        ),
        "phases": [
            {"label": "Alpha Settling",       "beat": 10.0, "carrier": 200.0, "minutes": 5},
            {"label": "Theta Descent",        "beat": 5.5,  "carrier": 190.0, "minutes": 5},
            {"label": "Deep Theta Hold",      "beat": 4.5,  "carrier": 185.0, "minutes": 20},
            {"label": "Gentle Return",        "beat": 8.0,  "carrier": 196.0, "minutes": 3},
        ],
    },
    "obe_attempt": {
        "name": "OBE Induction Protocol",
        "description": (
            "Full-depth session targeting Focus 21. Progressive descent\n"
            "  through all threshold states. For experienced practitioners\n"
            "  who have already felt the vibrational state."
        ),
        "phases": [
            {"label": "Body Settling",        "beat": 10.0, "carrier": 200.0, "minutes": 5},
            {"label": "Focus 10",             "beat": 10.0, "carrier": 200.0, "minutes": 8},
            {"label": "Focus 12",             "beat": 6.0,  "carrier": 196.0, "minutes": 8},
            {"label": "Focus 15 — No Time",   "beat": 4.5,  "carrier": 185.0, "minutes": 10},
            {"label": "Focus 21 — Bridge",    "beat": 2.5,  "carrier": 175.0, "minutes": 15},
            {"label": "Return: F12",          "beat": 6.0,  "carrier": 196.0, "minutes": 3},
            {"label": "Return: F10",          "beat": 10.0, "carrier": 200.0, "minutes": 2},
            {"label": "Return: Waking",       "beat": 14.0, "carrier": 200.0, "minutes": 2},
        ],
    },
    "gamma_clarity": {
        "name": "Gamma Clarity",
        "description": (
            "40Hz gamma entrainment for heightened cognition, insight,\n"
            "  and perceptual clarity. Research-backed frequency for\n"
            "  enhanced memory and attention."
        ),
        "phases": [
            {"label": "Alpha Baseline",       "beat": 10.0, "carrier": 200.0, "minutes": 3},
            {"label": "Beta Ramp",            "beat": 20.0, "carrier": 200.0, "minutes": 3},
            {"label": "Gamma Hold (40Hz)",    "beat": 40.0, "carrier": 200.0, "minutes": 20},
            {"label": "Alpha Return",         "beat": 10.0, "carrier": 200.0, "minutes": 3},
        ],
    },
    "sleep_descent": {
        "name": "Sleep Descent",
        "description": (
            "Gentle descent from waking into delta for sleep.\n"
            "  Not for practice — for rest."
        ),
        "phases": [
            {"label": "Alpha Settling",       "beat": 10.0, "carrier": 180.0, "minutes": 5},
            {"label": "Theta Drift",          "beat": 6.0,  "carrier": 175.0, "minutes": 10},
            {"label": "Deep Theta",           "beat": 4.0,  "carrier": 170.0, "minutes": 10},
            {"label": "Delta",                "beat": 2.0,  "carrier": 165.0, "minutes": 20},
        ],
    },
}

# ─────────────────────────────────────────────────────────────
# AMBIENT SOUND GENERATORS
# ─────────────────────────────────────────────────────────────

class PinkNoiseGenerator:
    """
    Stateful pink noise using the Voss-McCartney algorithm.
    Maintains state between calls so there are no discontinuities
    between audio buffers.
    """

    def __init__(self, num_rows=16):
        self.num_rows = num_rows
        self.max_key = (1 << num_rows) - 1
        self.key = 0
        self.rows = np.zeros(num_rows)
        self.running_sum = 0.0

    def generate(self, num_samples):
        samples = np.zeros(num_samples)
        for i in range(num_samples):
            self.key += 1
            if self.key > self.max_key:
                self.key = 0
            # Find which rows to update (trailing zeros of key)
            changed = self.key ^ (self.key - 1) if self.key > 0 else self.max_key
            for row in range(self.num_rows):
                if changed & (1 << row):
                    self.running_sum -= self.rows[row]
                    new_val = np.random.uniform(-1, 1)
                    self.running_sum += new_val
                    self.rows[row] = new_val
            # Add white noise component for high-frequency detail
            samples[i] = (self.running_sum + np.random.uniform(-1, 1)) / (self.num_rows + 1)
        return samples * 0.04  # Gentle background level


class BrownNoiseGenerator:
    """
    Stateful brown noise (random walk with drift correction).
    Maintains state between calls for seamless buffers.
    """

    def __init__(self):
        self.value = 0.0

    def generate(self, num_samples):
        samples = np.zeros(num_samples)
        for i in range(num_samples):
            self.value += np.random.uniform(-0.02, 0.02)
            # Gentle drift back toward zero to prevent runaway
            self.value *= 0.999
            self.value = np.clip(self.value, -1.0, 1.0)
            samples[i] = self.value
        return samples * 0.035


def silence_generator(num_samples):
    """No ambient — pure binaural signal only."""
    return np.zeros(num_samples)


AMBIENT_OPTIONS = {
    "none": {"name": "None (Pure Binaural)", "generator_type": "silence"},
    "pink": {"name": "Pink Noise", "generator_type": "pink"},
    "brown": {"name": "Brown Noise (Deep)", "generator_type": "brown"},
}

# ─────────────────────────────────────────────────────────────
# AUDIO ENGINE
# ─────────────────────────────────────────────────────────────

class BinauralEngine:
    """
    Real-time binaural beat generator using sounddevice.

    Generates stereo audio where:
      - Left ear: carrier_freq
      - Right ear: carrier_freq + beat_freq

    The brain perceives the difference as a pulsating beat at beat_freq Hz,
    which can entrain brainwave activity toward the target state.
    """

    SAMPLE_RATE = 44100

    # Tone generation modes
    MODE_BINAURAL = "binaural"
    MODE_ISOCHRONIC = "isochronic"
    MODE_BOTH = "both"

    MODES = {
        "binaural": {
            "name": "Binaural Beats",
            "description": "Stereo frequency difference — requires headphones",
        },
        "isochronic": {
            "name": "Isochronic Tones",
            "description": "Rhythmic on/off pulsing — works with speakers or headphones",
        },
        "both": {
            "name": "Binaural + Isochronic",
            "description": "Both methods layered together — requires headphones",
        },
    }

    def __init__(self):
        self.carrier_freq = 200.0
        self.beat_freq = 10.0
        self.volume = 0.3
        self.ambient_type = "none"
        self.tone_mode = self.MODE_BINAURAL
        self.iso_duty_cycle = 0.5    # Fraction of pulse that is "on" (0.3–0.7)
        self.iso_ramp_frac = 0.15    # Fraction of on-period used for fade in/out
        self.playing = False
        self.phase_left = 0.0
        self.phase_right = 0.0
        self.phase_carrier = 0.0     # Carrier phase for isochronic mode
        self.phase_pulse = 0.0       # Pulse envelope phase for isochronic mode
        self._stream = None
        self._lock = threading.Lock()

        # Stateful ambient generators (persist between buffers)
        self._pink_gen = PinkNoiseGenerator()
        self._brown_gen = BrownNoiseGenerator()

        # For session presets
        self._session_thread = None
        self._session_running = False
        self._current_phase_label = ""
        self._session_time_remaining = 0
        self._phase_time_remaining = 0

        # Smooth transitions
        self._target_beat = 10.0
        self._target_carrier = 200.0
        self._transition_speed = 0.5  # Hz per second

    def _generate_binaural(self, frames, carrier, beat):
        """Generate stereo binaural beat signal."""
        t = np.arange(frames) / self.SAMPLE_RATE
        freq_left = carrier
        freq_right = carrier + beat

        left = np.sin(2 * np.pi * freq_left * t + self.phase_left)
        right = np.sin(2 * np.pi * freq_right * t + self.phase_right)

        self.phase_left = (self.phase_left + 2 * np.pi * freq_left * frames / self.SAMPLE_RATE) % (2 * np.pi)
        self.phase_right = (self.phase_right + 2 * np.pi * freq_right * frames / self.SAMPLE_RATE) % (2 * np.pi)

        return left, right

    def _generate_isochronic(self, frames, carrier, beat):
        """
        Generate isochronic tone — a carrier pulsed on/off at the beat frequency.

        The envelope uses smooth ramps (raised cosine) to avoid clicks.
        The pulse is mono (same in both ears) since isochronic tones
        don't rely on stereo separation.
        """
        t = np.arange(frames) / self.SAMPLE_RATE
        duty = self.iso_duty_cycle
        ramp = self.iso_ramp_frac

        # Carrier tone (continuous phase)
        tone = np.sin(2 * np.pi * carrier * t + self.phase_carrier)
        self.phase_carrier = (self.phase_carrier + 2 * np.pi * carrier * frames / self.SAMPLE_RATE) % (2 * np.pi)

        # Pulse envelope at beat frequency
        # Phase progresses through [0, 1) for each pulse cycle
        pulse_phase = np.zeros(frames)
        for i in range(frames):
            pulse_phase[i] = self.phase_pulse
            self.phase_pulse += beat / self.SAMPLE_RATE
            if self.phase_pulse >= 1.0:
                self.phase_pulse -= 1.0

        # Build smooth envelope: on for duty fraction, off for the rest
        envelope = np.zeros(frames)
        for i in range(frames):
            p = pulse_phase[i]
            if p < duty:
                # Inside the "on" portion
                pos_in_on = p / duty  # 0 to 1 within the on-period
                if pos_in_on < ramp:
                    # Fade in (raised cosine)
                    envelope[i] = 0.5 * (1.0 - np.cos(np.pi * pos_in_on / ramp))
                elif pos_in_on > (1.0 - ramp):
                    # Fade out (raised cosine)
                    envelope[i] = 0.5 * (1.0 - np.cos(np.pi * (1.0 - pos_in_on) / ramp))
                else:
                    envelope[i] = 1.0
            # else: envelope stays 0 (off portion)

        signal = tone * envelope
        return signal, signal  # Mono — same in both ears

    def _audio_callback(self, outdata, frames, time_info, status):
        """Called by sounddevice to fill the audio buffer."""
        with self._lock:
            beat = self.beat_freq
            carrier = self.carrier_freq
            vol = self.volume
            ambient_key = self.ambient_type
            mode = self.tone_mode

        # Smooth frequency transitions
        self._approach_target()

        # Generate signal based on tone mode
        if mode == self.MODE_BINAURAL:
            left, right = self._generate_binaural(frames, carrier, beat)
        elif mode == self.MODE_ISOCHRONIC:
            left, right = self._generate_isochronic(frames, carrier, beat)
        else:
            # Both modes layered
            bl, br = self._generate_binaural(frames, carrier, beat)
            il, ir = self._generate_isochronic(frames, carrier, beat)
            left = bl * 0.6 + il * 0.4
            right = br * 0.6 + ir * 0.4

        # Apply volume
        left *= vol
        right *= vol

        # Add ambient to both channels (stateful generators — no discontinuities)
        if ambient_key == "pink":
            ambient = self._pink_gen.generate(frames) * vol
        elif ambient_key == "brown":
            ambient = self._brown_gen.generate(frames) * vol
        else:
            ambient = np.zeros(frames)
        left += ambient
        right += ambient

        # Clip and write stereo output
        outdata[:, 0] = np.clip(left, -1.0, 1.0)
        outdata[:, 1] = np.clip(right, -1.0, 1.0)

    def _approach_target(self):
        """Smoothly transition current frequencies toward targets."""
        step = self._transition_speed * 1024 / self.SAMPLE_RATE  # per buffer

        with self._lock:
            if abs(self.beat_freq - self._target_beat) > 0.01:
                if self.beat_freq < self._target_beat:
                    self.beat_freq = min(self.beat_freq + step, self._target_beat)
                else:
                    self.beat_freq = max(self.beat_freq - step, self._target_beat)

            if abs(self.carrier_freq - self._target_carrier) > 0.01:
                if self.carrier_freq < self._target_carrier:
                    self.carrier_freq = min(self.carrier_freq + step * 2, self._target_carrier)
                else:
                    self.carrier_freq = max(self.carrier_freq - step * 2, self._target_carrier)

    def set_frequencies(self, beat_freq, carrier_freq=None):
        """Set target frequencies — engine transitions smoothly."""
        with self._lock:
            self._target_beat = beat_freq
            if carrier_freq is not None:
                self._target_carrier = carrier_freq

    def set_volume(self, volume):
        with self._lock:
            self.volume = max(0.0, min(1.0, volume))

    def set_mode(self, mode):
        with self._lock:
            if mode in self.MODES:
                self.tone_mode = mode

    def set_ambient(self, ambient_key):
        with self._lock:
            if ambient_key in AMBIENT_OPTIONS:
                self.ambient_type = ambient_key

    def start(self):
        """Begin audio output."""
        if self.playing:
            return
        if not AUDIO_AVAILABLE:
            print(f"\n  {RED}Audio unavailable — install portaudio and sounddevice.{RESET}")
            print(f"  {DIM}  macOS:  brew install portaudio && pip install sounddevice{RESET}")
            print(f"  {DIM}  Linux:  sudo apt install portaudio19-dev && pip install sounddevice{RESET}")
            print(f"  {DIM}  Windows: pip install sounddevice{RESET}")
            time.sleep(2)
            return
        self.playing = True
        self._stream = sd.OutputStream(
            samplerate=self.SAMPLE_RATE,
            channels=2,
            callback=self._audio_callback,
            blocksize=1024,
        )
        self._stream.start()

    def stop(self):
        """Stop audio output."""
        self._session_running = False
        self.playing = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def run_session(self, preset_key, on_phase_change=None):
        """Run a multi-phase session preset in a background thread."""
        preset = SESSION_PRESETS[preset_key]
        self._session_running = True

        def session_worker():
            phases = preset["phases"]
            total_seconds = sum(p["minutes"] * 60 for p in phases)
            elapsed_total = 0

            for i, phase in enumerate(phases):
                if not self._session_running:
                    break

                self._current_phase_label = phase["label"]
                phase_seconds = phase["minutes"] * 60
                self.set_frequencies(phase["beat"], phase["carrier"])

                if on_phase_change:
                    on_phase_change(phase["label"], i + 1, len(phases))

                for sec in range(phase_seconds):
                    if not self._session_running:
                        break
                    self._phase_time_remaining = phase_seconds - sec
                    self._session_time_remaining = total_seconds - elapsed_total - sec
                    time.sleep(1)

                elapsed_total += phase_seconds

            self._session_running = False
            self._current_phase_label = "Complete"

        if not self.playing:
            self.start()

        self._session_thread = threading.Thread(target=session_worker, daemon=True)
        self._session_thread.start()

    def stop_session(self):
        self._session_running = False

    @property
    def session_running(self):
        return self._session_running

    @property
    def current_phase(self):
        return self._current_phase_label

    @property
    def session_time_remaining(self):
        return self._session_time_remaining

    @property
    def phase_time_remaining(self):
        return self._phase_time_remaining


# ─────────────────────────────────────────────────────────────
# TERMINAL UI
# ─────────────────────────────────────────────────────────────

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
WHITE = "\033[37m"
RED = "\033[31m"


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def banner():
    print(f"""
{MAGENTA}{BOLD}  ╔══════════════════════════════════════════════════════╗
  ║       BRAINWAVE ENTRAINMENT — CONSCIOUSNESS MAP      ║
  ║                  State Navigator                     ║
  ╚══════════════════════════════════════════════════════╝{RESET}
{DIM}  Headphones required for binaural beats. Close your eyes.{RESET}
""")


def get_band_for_freq(freq):
    """Return the brainwave band name for a given frequency."""
    for name, band in BRAINWAVE_BANDS.items():
        if band["range"][0] <= freq <= band["range"][1]:
            return name
    if freq < 0.5:
        return "sub-delta"
    return "gamma"


def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def print_status(engine):
    """Print current engine state."""
    band = get_band_for_freq(engine.beat_freq)
    band_info = BRAINWAVE_BANDS.get(band, {"color": WHITE, "description": ""})
    color = band_info["color"]

    mode_name = BinauralEngine.MODES[engine.tone_mode]["name"]

    print(f"\n  {BOLD}Current State{RESET}")
    print(f"  {DIM}────────────────────────────────{RESET}")
    print(f"  Mode:            {BOLD}{mode_name}{RESET}")
    print(f"  Beat Frequency:  {color}{BOLD}{engine.beat_freq:.1f} Hz{RESET} ({band})")
    print(f"  Carrier Tone:    {engine.carrier_freq:.1f} Hz")
    print(f"  Volume:          {'█' * int(engine.volume * 20)}{'░' * (20 - int(engine.volume * 20))} {int(engine.volume * 100)}%")
    print(f"  Ambient:         {AMBIENT_OPTIONS[engine.ambient_type]['name']}")
    print(f"  Band:            {color}{band_info['description']}{RESET}")

    if engine.session_running:
        print(f"\n  {GREEN}{BOLD}Session Active{RESET}")
        print(f"  Phase:           {engine.current_phase}")
        print(f"  Phase remaining: {format_time(engine.phase_time_remaining)}")
        print(f"  Total remaining: {format_time(engine.session_time_remaining)}")


def main_menu(engine):
    """Display main menu and return choice."""
    print(f"\n  {BOLD}Navigation{RESET}")
    print(f"  {DIM}────────────────────────────────{RESET}")
    print(f"  {CYAN}[1]{RESET} Monroe Focus Levels")
    print(f"  {CYAN}[2]{RESET} Brainwave States (manual)")
    print(f"  {CYAN}[3]{RESET} Session Presets")
    print(f"  {CYAN}[4]{RESET} Custom Frequency")
    print(f"  {DIM}────────────────────────────────{RESET}")
    print(f"  {CYAN}[v]{RESET} Adjust Volume")
    print(f"  {CYAN}[a]{RESET} Change Ambient Sound")
    print(f"  {CYAN}[m]{RESET} Tone Mode ({BinauralEngine.MODES[engine.tone_mode]['name']})")
    if engine.playing:
        print(f"  {CYAN}[s]{RESET} Stop Audio")
    if engine.session_running:
        print(f"  {RED}[x]{RESET} Stop Session")
    print(f"  {CYAN}[q]{RESET} Quit")
    print()
    return input(f"  {BOLD}>{RESET} ").strip().lower()


def focus_level_menu(engine):
    """Monroe Focus Level selection."""
    clear()
    banner()
    print(f"  {MAGENTA}{BOLD}MONROE FOCUS LEVELS{RESET}")
    print(f"  {DIM}Mapped from the Gateway Experience framework.{RESET}")
    print(f"  {DIM}Each level targets a specific depth of consciousness.{RESET}\n")

    keys = list(FOCUS_LEVELS.keys())
    for i, key in enumerate(keys):
        fl = FOCUS_LEVELS[key]
        band = get_band_for_freq(fl["beat_freq"])
        color = BRAINWAVE_BANDS.get(band, {"color": WHITE})["color"]
        print(f"  {CYAN}[{i + 1}]{RESET} {color}{BOLD}{fl['name']}{RESET}")
        print(f"      {DIM}{fl['description']}{RESET}")
        print(f"      Beat: {fl['beat_freq']} Hz ({band}) | Carrier: {fl['carrier_freq']} Hz | Default: {fl['duration_default']} min")
        print()

    print(f"  {CYAN}[b]{RESET} Back\n")
    choice = input(f"  {BOLD}>{RESET} ").strip().lower()

    if choice == "b":
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(keys):
            fl = FOCUS_LEVELS[keys[idx]]
            engine.set_frequencies(fl["beat_freq"], fl["carrier_freq"])
            if not engine.playing:
                engine.start()
            print(f"\n  {GREEN}▶ Now targeting: {fl['name']}{RESET}")
            time.sleep(1.5)
    except (ValueError, IndexError):
        pass


def brainwave_menu(engine):
    """Manual brainwave state selection."""
    clear()
    banner()
    print(f"  {BLUE}{BOLD}BRAINWAVE STATES{RESET}")
    print(f"  {DIM}Select a brainwave band. The beat frequency will be set{RESET}")
    print(f"  {DIM}to the center of the selected range.{RESET}\n")

    keys = list(BRAINWAVE_BANDS.keys())
    for i, key in enumerate(keys):
        band = BRAINWAVE_BANDS[key]
        lo, hi = band["range"]
        center = (lo + hi) / 2
        print(f"  {CYAN}[{i + 1}]{RESET} {band['color']}{BOLD}{key.upper()}{RESET} ({lo}–{hi} Hz)")
        print(f"      {DIM}{band['description']}{RESET}")
        print(f"      Center frequency: {center:.1f} Hz")
        print()

    print(f"  {CYAN}[b]{RESET} Back\n")
    choice = input(f"  {BOLD}>{RESET} ").strip().lower()

    if choice == "b":
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(keys):
            band = BRAINWAVE_BANDS[keys[idx]]
            lo, hi = band["range"]
            center = (lo + hi) / 2
            engine.set_frequencies(center)
            if not engine.playing:
                engine.start()
            print(f"\n  {GREEN}▶ Entraining to: {keys[idx].upper()} ({center:.1f} Hz){RESET}")
            time.sleep(1.5)
    except (ValueError, IndexError):
        pass


def session_menu(engine):
    """Session preset selection."""
    clear()
    banner()
    print(f"  {GREEN}{BOLD}SESSION PRESETS{RESET}")
    print(f"  {DIM}Multi-phase protocols that transition between states.{RESET}")
    print(f"  {DIM}Sit back and let the session guide you.{RESET}\n")

    keys = list(SESSION_PRESETS.keys())
    for i, key in enumerate(keys):
        preset = SESSION_PRESETS[key]
        total_min = sum(p["minutes"] for p in preset["phases"])
        print(f"  {CYAN}[{i + 1}]{RESET} {BOLD}{preset['name']}{RESET} ({total_min} min)")
        print(f"      {DIM}{preset['description']}{RESET}")

        # Show phase timeline
        timeline = " → ".join(
            f"{p['label']} ({p['minutes']}m)" for p in preset["phases"]
        )
        print(f"      {DIM}Phases: {timeline}{RESET}")
        print()

    print(f"  {CYAN}[b]{RESET} Back\n")
    choice = input(f"  {BOLD}>{RESET} ").strip().lower()

    if choice == "b":
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(keys):
            preset_key = keys[idx]
            preset = SESSION_PRESETS[preset_key]
            total_min = sum(p["minutes"] for p in preset["phases"])

            print(f"\n  {GREEN}▶ Starting: {preset['name']} ({total_min} min){RESET}")
            print(f"  {DIM}  Press Ctrl+C to return to menu at any time.{RESET}")

            def on_phase(label, num, total):
                print(f"\r  {YELLOW}Phase {num}/{total}: {label}{RESET}          ", end="", flush=True)

            engine.run_session(preset_key, on_phase_change=on_phase)
            time.sleep(2)
    except (ValueError, IndexError):
        pass


def custom_freq_menu(engine):
    """Set a custom binaural beat frequency."""
    clear()
    banner()
    print(f"  {YELLOW}{BOLD}CUSTOM FREQUENCY{RESET}")
    print(f"  {DIM}Set any binaural beat frequency (0.5–44 Hz).{RESET}")
    print(f"  {DIM}Optionally set the carrier tone (100–500 Hz).{RESET}\n")

    try:
        beat_str = input(f"  Beat frequency (Hz): ").strip()
        if not beat_str:
            return
        beat = float(beat_str)
        beat = max(0.5, min(44.0, beat))

        carrier_str = input(f"  Carrier frequency (Hz) [default: 200]: ").strip()
        carrier = float(carrier_str) if carrier_str else 200.0
        carrier = max(100.0, min(500.0, carrier))

        engine.set_frequencies(beat, carrier)
        if not engine.playing:
            engine.start()

        band = get_band_for_freq(beat)
        print(f"\n  {GREEN}▶ Set to {beat:.1f} Hz ({band}) with carrier {carrier:.1f} Hz{RESET}")
        time.sleep(1.5)
    except ValueError:
        print(f"  {RED}Invalid input.{RESET}")
        time.sleep(1)


def volume_menu(engine):
    """Adjust volume."""
    try:
        current = int(engine.volume * 100)
        val = input(f"\n  Volume (0–100) [current: {current}]: ").strip()
        if val:
            engine.set_volume(int(val) / 100.0)
            print(f"  {GREEN}Volume set to {int(engine.volume * 100)}%{RESET}")
            time.sleep(0.8)
    except ValueError:
        pass


def ambient_menu(engine):
    """Change ambient sound."""
    print(f"\n  {BOLD}Ambient Sound{RESET}")
    keys = list(AMBIENT_OPTIONS.keys())
    for i, key in enumerate(keys):
        marker = " ◀" if key == engine.ambient_type else ""
        print(f"  {CYAN}[{i + 1}]{RESET} {AMBIENT_OPTIONS[key]['name']}{marker}")

    try:
        choice = input(f"\n  {BOLD}>{RESET} ").strip()
        idx = int(choice) - 1
        if 0 <= idx < len(keys):
            engine.set_ambient(keys[idx])
            print(f"  {GREEN}Ambient: {AMBIENT_OPTIONS[keys[idx]]['name']}{RESET}")
            time.sleep(0.8)
    except (ValueError, IndexError):
        pass


def mode_menu(engine):
    """Switch between binaural, isochronic, and combined modes."""
    print(f"\n  {BOLD}Tone Mode{RESET}")
    keys = list(BinauralEngine.MODES.keys())
    for i, key in enumerate(keys):
        info = BinauralEngine.MODES[key]
        marker = " ◀" if key == engine.tone_mode else ""
        print(f"  {CYAN}[{i + 1}]{RESET} {BOLD}{info['name']}{RESET}{marker}")
        print(f"      {DIM}{info['description']}{RESET}")

    try:
        choice = input(f"\n  {BOLD}>{RESET} ").strip()
        idx = int(choice) - 1
        if 0 <= idx < len(keys):
            engine.set_mode(keys[idx])
            info = BinauralEngine.MODES[keys[idx]]
            print(f"  {GREEN}Mode: {info['name']}{RESET}")
            time.sleep(0.8)
    except (ValueError, IndexError):
        pass


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    engine = BinauralEngine()

    # Graceful shutdown
    def signal_handler(sig, frame):
        engine.stop()
        print(f"\n\n  {DIM}Session ended.{RESET}\n")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        try:
            clear()
            banner()
            if engine.playing:
                print_status(engine)
            main_choice = main_menu(engine)

            if main_choice == "1":
                focus_level_menu(engine)
            elif main_choice == "2":
                brainwave_menu(engine)
            elif main_choice == "3":
                session_menu(engine)
            elif main_choice == "4":
                custom_freq_menu(engine)
            elif main_choice == "v":
                volume_menu(engine)
            elif main_choice == "a":
                ambient_menu(engine)
            elif main_choice == "m":
                mode_menu(engine)
            elif main_choice == "s":
                engine.stop()
                print(f"  {DIM}Audio stopped.{RESET}")
                time.sleep(0.8)
            elif main_choice == "x":
                engine.stop_session()
                print(f"  {DIM}Session stopped.{RESET}")
                time.sleep(0.8)
            elif main_choice == "q":
                engine.stop()
                print(f"\n  {DIM}Safe travels.{RESET}\n")
                break
        except KeyboardInterrupt:
            engine.stop()
            print(f"\n\n  {DIM}Session ended.{RESET}\n")
            break


if __name__ == "__main__":
    main()
