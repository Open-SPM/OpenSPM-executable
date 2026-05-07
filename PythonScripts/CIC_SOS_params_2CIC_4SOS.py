import numpy as np
from scipy import signal
import math

# import matplotlib.pyplot as plt

# ============================================================
# DESIGN CONSTANTS
# ============================================================

FS_MIN = 10.0        # Minimum Fs after decimation (Hz)
K_FC   = 15.0        # Target Fs_out ≈ K_FC * fc
MAX_K1 = 10          # CIC1 max = 2^10 = 1024

# ============================================================
# INTERNAL DESIGN CORE
# ============================================================

def _compute_full_design(Fs_in, fc):
    """
    Internal helper.
    Computes:
      - CIC decimation exponents k1, k2 (R1=2^k1, R2=2^k2)
      - Full 4-SOS Butterworth LPF (order 8)
    Returns ONLY Python scalars and fixed-size arrays.
    """

    # -------- Clamp inputs --------
    Fs_in = min(max(float(Fs_in), 1e6), 80e6)
    fc    = min(max(float(fc), 1.0), 20e6)

    # -------- Target output Fs --------
    Fs_target = max(K_FC * fc, FS_MIN)
    Fs_target = min(Fs_target, Fs_in)

    # -------- Total decimation (power of two) --------
    k_total = int(round(math.log2(Fs_in / Fs_target)))
    k_total = max(0, k_total)

    # -------- Split across two CICs --------
    k1 = min(MAX_K1, k_total)
    k2 = max(0, k_total - k1)

    R1 = 2 ** k1
    R2 = 2 ** k2

    Fs_eff = Fs_in / (R1 * R2)

    # -------- IIR design (8th order Butterworth) --------
    wn = fc / (Fs_eff / 2.0)
    wn = min(max(wn, 1e-6), 0.999999)

    sos = signal.butter(
        N=8,
        Wn=wn,
        btype="low",
        output="sos"
    )

    # -------- Normalize total DC gain to 1 --------
    _, h0 = signal.sosfreqz(sos, worN=[0])
    gain = abs(h0[0])
    sos[0, 0:3] /= gain

    return k1, k2, sos


# ============================================================
# CIC DECIMATION (EXPONENTS)
# ============================================================

def get_cic_k1(Fs_in, fc):
    return _compute_full_design(Fs_in, fc)[0]

def get_cic_k2(Fs_in, fc):
    return _compute_full_design(Fs_in, fc)[1]


# ============================================================
# SOS 1
# ============================================================

def get_sos1_b0(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][0, 0]
def get_sos1_b1(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][0, 1]
def get_sos1_b2(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][0, 2]
def get_sos1_a1(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][0, 4]
def get_sos1_a2(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][0, 5]

# ============================================================
# SOS 2
# ============================================================

def get_sos2_b0(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][1, 0]
def get_sos2_b1(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][1, 1]
def get_sos2_b2(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][1, 2]
def get_sos2_a1(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][1, 4]
def get_sos2_a2(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][1, 5]

# ============================================================
# SOS 3
# ============================================================

def get_sos3_b0(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][2, 0]
def get_sos3_b1(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][2, 1]
def get_sos3_b2(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][2, 2]
def get_sos3_a1(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][2, 4]
def get_sos3_a2(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][2, 5]

# ============================================================
# SOS 4
# ============================================================

def get_sos4_b0(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][3, 0]
def get_sos4_b1(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][3, 1]
def get_sos4_b2(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][3, 2]
def get_sos4_a1(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][3, 4]
def get_sos4_a2(Fs_in, fc): return _compute_full_design(Fs_in, fc)[2][3, 5]


# # ------------------------------------------------------------
# # PARAMETERS TO TEST
# # ------------------------------------------------------------

# Fs_in = 20e6      # 20 MHz input sampling
# fc    = 10e3       # 1 kHz low-pass cutoff

# # ------------------------------------------------------------
# # GET CIC DECIMATION (EXPONENTS)
# # ------------------------------------------------------------

# k1 = get_cic_k1(Fs_in, fc)
# k2 = get_cic_k2(Fs_in, fc)

# R1 = 2 ** k1
# R2 = 2 ** k2

# Fs_eff = Fs_in / (R1 * R2)

# print("Input Fs       :", Fs_in, "Hz")
# print("Cutoff fc      :", fc, "Hz")
# print("CIC1 k1        :", k1, " -> R1 =", R1)
# print("CIC2 k2        :", k2, " -> R2 =", R2)
# print("Effective Fs   :", Fs_eff, "Hz")

# # ------------------------------------------------------------
# # REBUILD FULL SOS MATRIX
# # ------------------------------------------------------------

# sos = np.zeros((4, 6))

# # SOS 1
# sos[0] = [
#     get_sos1_b0(Fs_in, fc),
#     get_sos1_b1(Fs_in, fc),
#     get_sos1_b2(Fs_in, fc),
#     1.0,
#     get_sos1_a1(Fs_in, fc),
#     get_sos1_a2(Fs_in, fc),
# ]

# # SOS 2
# sos[1] = [
#     get_sos2_b0(Fs_in, fc),
#     get_sos2_b1(Fs_in, fc),
#     get_sos2_b2(Fs_in, fc),
#     1.0,
#     get_sos2_a1(Fs_in, fc),
#     get_sos2_a2(Fs_in, fc),
# ]

# # SOS 3
# sos[2] = [
#     get_sos3_b0(Fs_in, fc),
#     get_sos3_b1(Fs_in, fc),
#     get_sos3_b2(Fs_in, fc),
#     1.0,
#     get_sos3_a1(Fs_in, fc),
#     get_sos3_a2(Fs_in, fc),
# ]

# # SOS 4
# sos[3] = [
#     get_sos4_b0(Fs_in, fc),
#     get_sos4_b1(Fs_in, fc),
#     get_sos4_b2(Fs_in, fc),
#     1.0,
#     get_sos4_a1(Fs_in, fc),
#     get_sos4_a2(Fs_in, fc),
# ]

# print("\nSOS matrix:")
# print(sos)

# # ------------------------------------------------------------
# # CHECK DC GAIN
# # ------------------------------------------------------------

# _, h0 = signal.sosfreqz(sos, worN=[0], fs=Fs_eff)
# print("\nDC gain =", abs(h0[0]))

# # ------------------------------------------------------------
# # FREQUENCY RESPONSE
# # ------------------------------------------------------------

# w, h = signal.sosfreqz(sos, worN=8192, fs=Fs_eff)

# plt.figure(figsize=(8, 5))
# plt.semilogx(w, 20 * np.log10(np.maximum(np.abs(h), 1e-12)))
# plt.axvline(fc, color='r', linestyle='--', label='fc')
# plt.grid(True, which='both')
# plt.xlabel("Frequency [Hz]")
# plt.ylabel("Magnitude [dB]")
# plt.title("Final 8th-order Butterworth LPF (after 2 CIC decimators)")
# plt.legend()
# plt.tight_layout()
# plt.show()
