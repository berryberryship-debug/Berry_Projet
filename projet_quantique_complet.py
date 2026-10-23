import numpy as np
from dataclasses import dataclass

# ==========================================
# 1. IMPULSIONS
# ==========================================
def gaussian(t, t0, sigma, amplitude=1.0):
    return amplitude * np.exp(-((t - t0)**2) / (2 * sigma**2))

# ==========================================
# 2. BRUIT
# ==========================================
def generate_1f_noise(n_samples, dt=1.0, seed=None):
    if seed is not None: np.random.seed(seed)
    white = np.random.randn(n_samples)
    f = np.fft.rfftfreq(n_samples, d=dt)
    f[0] = f[1]
    s_filter = 1.0 / np.sqrt(f)
    s_filter[0] = 0.0
    noise_fft = np.fft.rfft(white) * s_filter
    noise = np.fft.irfft(noise_fft, n=n_samples)
    return noise / (np.std(noise) + 1e-12)

# ==========================================
# 3. MOIRÉ
# ==========================================
@dataclass(frozen=True)
class MoireField:
    k1: tuple
    k2: tuple
    amplitude: float = 1.0
    def sample(self, x, y, t=0.0):
        return self.amplitude * (np.cos(self.k1[0]*x + self.k1[1]*y) + np.cos(self.k2[0]*x + self.k2[1]*y))

def gaussian_weight(x, y, x0, y0, sigma_device):
    r2 = (x - x0) ** 2 + (y - y0) ** 2
    return np.exp(-r2 / (2.0 * sigma_device ** 2))

def effective_field(field, x, y, t, x0, y0, sigma_device):
    weights = gaussian_weight(x, y, x0, y0, sigma_device)
    values = field.sample(x, y, t)
    return float(np.sum(weights * values) / np.sum(weights))

# ==========================================
# 4. MÉTRIQUES
# ==========================================
def state_fidelity(psi_target, psi_achieved):
    overlap = np.vdot(psi_target, psi_achieved)
    return float(np.abs(overlap)**2)

# ==========================================
# 5. SYSTÈME TRANSMON
# ==========================================
@dataclass
class TransmonSystem:
    omega_q: float = 5.0
    anharmonicity: float = -0.3
    n_levels: int = 3

    def _get_operators(self):
        N = self.n_levels
        a = np.diag(np.sqrt(np.arange(1, N)), k=1).astype(complex)
        return a, a.conj().T

    def _get_hamiltonian_base(self):
        N = self.n_levels
        E = np.zeros(N)
        for n in range(N):
            E[n] = n * self.omega_q + (n * (n - 1) / 2.0) * self.anharmonicity
        return np.diag(E).astype(complex)

    def simulate(self, t, pulse, noise=None):
        dt = t[1] - t[0]
        n_steps = len(t)
        psi_0 = np.zeros(self.n_levels, dtype=complex)
        psi_0[0] = 1.0
        trajectory = np.zeros((self.n_levels, n_steps), dtype=complex)
        trajectory[:, 0] = psi_0
        H0 = self._get_hamiltonian_base()
        a, a_dag = self._get_operators()
        X_op = a + a_dag 
        current_psi = psi_0.copy()
        
        for i in range(1, n_steps):
            signal = pulse[i] if i < len(pulse) else 0.0
            if noise is not None and i < len(noise):
                signal += noise[i]
            H = H0 + signal * X_op
            eigvals, eigvecs = np.linalg.eigh(H)
            U = eigvecs @ np.diag(np.exp(-1j * eigvals * dt)) @ eigvecs.conj().T
            current_psi = U @ current_psi
            trajectory[:, i] = current_psi
        return trajectory

# ==========================================
# 6. LANCEUR PRINCIPAL
# ==========================================
def main():
    print("==================================================")
    print("TEST DU MOTEUR QUANTIQUE (VERSION FICHIER UNIQUE)")
    print("==================================================")
    
    t = np.linspace(0, 20, 1000)
    dt = t[1] - t[0]
    system = TransmonSystem()
    
    pulse = gaussian(t, t0=10, sigma=3, amplitude=1)
    noise = generate_1f_noise(len(t), dt=dt, seed=42) * 0.05
    
    print("[+] Simulation de l'évolution du qubit en cours...")
    traj = system.simulate(t, pulse, noise=noise)
    
    target = np.array([0.0, 1.0, 0.0], dtype=complex)
    final_state = traj[:, -1]
    norm = np.linalg.norm(final_state)
    normalized_state = final_state / norm if norm > 0 else final_state
    
    fidelity = state_fidelity(target, normalized_state)
    
    print("==================================================")
    print(f"Fidélité finale de la porte quantique : {fidelity:.6f}")
    print("==================================================")
    print("SUCCÈS : Le moteur quantique fonctionne !")

if __name__ == "__main__":
    main()
