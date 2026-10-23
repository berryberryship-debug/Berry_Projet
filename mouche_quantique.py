import numpy as np
# On importe les deux briques depuis tes autres fichiers
from projet_quantique_complet import TransmonSystem, gaussian, generate_1f_noise, state_fidelity
from cerveau_mouche_complet import GlobalWorkspace, Metacognition, EpisodicMemory, PredictiveModel, SelfModel, Episode

class MoucheQuantique:
    def __init__(self):
        self.systeme_quantique = TransmonSystem()
        self.workspace = GlobalWorkspace()
        self.metacognition = Metacognition()
        self.memoire = EpisodicMemory()
        self.modele_predictif = PredictiveModel()
        self.modele_soi = SelfModel()
        
        # L'état interne de la mouche : sa capacité à contrôler le qubit
        self.energie = 1.0 # Représente l'amplitude de l'impulsion
        self.danger = 0.0  # Représente le taux d'erreur (leakage/bruit)

    def evaluer_qubit(self, amplitude_impulsion):
        t = np.linspace(0, 20, 200)
        pulse = gaussian(t, t0=10, sigma=3, amplitude=amplitude_impulsion)
        noise = generate_1f_noise(len(t), dt=t[1]-t[0], seed=42) * 0.05
        
        traj = self.systeme_quantique.simulate(t, pulse, noise=noise)
        cible = np.array([0.0, 1.0, 0.0], dtype=complex)
        
        etat_final = traj[:, -1]
        norme = np.linalg.norm(etat_final)
        etat_normalise = etat_final / norme if norme > 0 else etat_final
        
        fidelite = state_fidelity(cible, etat_normalise)
        
        # Le "danger" pour la mouche, c'est l'infidélité (1 - fidélité)
        self.danger = 1.0 - fidelite 
        return fidelite

    def executer_cycle(self):
        print("==================================================")
        print("MOUCHE QUANTIQUE : COUPLAGE COGNITION-PHYSIQUE")
        print("==================================================")
        
        for temps in range(15):
            # 1. La mouche "ressent" le monde quantique (inférence active)
            fidelite_actuelle = self.evaluer_qubit(self.energie)
            
            # 2. Les idées se battent dans l'espace de travail
            self.workspace.soumettre("danger_quantique", self.danger, "qubit", {"fidelite": fidelite_actuelle})
            self.workspace.soumettre("manque_energie", 1.0 - self.energie, "soi", {"amplitude": self.energie})
            
            idee = self.workspace.diffuser()
            nom_idee = idee.nom if idee is not None else None
            
            # 3. Décision basée sur la conscience
            action = "maintenir"
            if nom_idee == "danger_quantique" and self.danger > 0.3:
                action = "augmenter_amplitude"
            elif nom_idee == "manque_energie" and self.energie < 0.5:
                action = "reduire_amplitude"

            # 4. Prédiction de l'effet de l'action
            prediction = self.modele_predictif.predict(self.energie, self.danger, action)
            
            # 5. Application de l'action (modification de l'impulsion)
            if action == "augmenter_amplitude":
                self.energie += 0.1
            elif action == "reduire_amplitude":
                self.energie -= 0.1
                
            self.energie = max(0.1, min(1.5, self.energie)) # Bornes physiques
            
            # 6. La mouche observe la conséquence (nouvelle fidélité)
            nouvelle_fidelite = self.evaluer_qubit(self.energie)
            
            # 7. Calcul de l'erreur (Surprise)
            erreur = self.modele_predictif.error(prediction, self.energie, self.danger)
            
            # 8. Mémorisation et Métacognition
            episode = Episode(
                time=temps,
                observation={"fidelite": nouvelle_fidelite, "amplitude": self.energie},
                action=action,
                consequence={"nouveau_danger": self.danger},
                surprise=erreur,
                valence=1.0 if nouvelle_fidelite > 0.8 else -1.0
            )
            self.memoire.remember(episode)
            self.metacognition.revise(f"{action} pour stabiliser le qubit", erreur)
            
            print(f"Tour {temps:2d} | Action: {action:20s} | Amplitude: {self.energie:.2f} | Fidélité: {nouvelle_fidelite:.3f}")

        print("\n===== RAPPORT FINAL DE LA MOUCHE QUANTIQUE =====")
        for croyance in self.metacognition.explain():
            print(" -", croyance)

if __name__ == "__main__":
    mouche = MoucheQuantique()
    mouche.executer_cycle()
