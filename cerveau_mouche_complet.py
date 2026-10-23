from dataclasses import dataclass, field

# ==========================================
# 1. ENVIRONNEMENT (Le Monde)
# ==========================================
@dataclass
class World:
    danger: float = 0.0
    light_level: float = 0.5
    temperature: float = 0.5
    food_density: float = 0.5

    def step(self, time: int) -> None:
        if time == 10: self.danger = 0.9
        if time == 25: self.danger = 0.1
        self.danger = max(0.0, min(1.0, self.danger))

# ==========================================
# 2. ESPACE DE TRAVAIL (Conscience)
# ==========================================
@dataclass
class Idee:
    nom: str
    activation: float
    source: str
    contenu: dict = field(default_factory=dict)

@dataclass
class GlobalWorkspace:
    seuil_broadcast: float = 0.35
    idee_active: Idee | None = None
    historique: list[Idee] = field(default_factory=list)

    def soumettre(self, nom: str, activation: float, source: str, contenu: dict | None = None) -> None:
        idee = Idee(nom=nom, activation=max(0.0, min(1.0, activation)), source=source, contenu=contenu or {})
        if self.idee_active is None or idee.activation > self.idee_active.activation:
            self.idee_active = idee

    def diffuser(self) -> Idee | None:
        if self.idee_active is None or self.idee_active.activation < self.seuil_broadcast:
            return None
        self.historique.append(self.idee_active)
        if len(self.historique) > 100: self.historique = self.historique[-100:]
        idee = self.idee_active
        self.idee_active = None
        return idee

# ==========================================
# 3. MÉTACOGNITION (Croyances)
# ==========================================
@dataclass
class Belief:
    statement: str
    confidence: float
    evidence: int = 1

@dataclass
class Metacognition:
    beliefs: dict[str, Belief] = field(default_factory=dict)

    def revise(self, statement: str, surprise: float) -> None:
        if statement not in self.beliefs:
            self.beliefs[statement] = Belief(statement=statement, confidence=0.5, evidence=1)
            return
        belief = self.beliefs[statement]
        belief.evidence += 1
        if surprise < 0.2:
            belief.confidence = min(1.0, belief.confidence + 0.08)
        else:
            belief.confidence = max(0.0, belief.confidence - 0.12)

    def explain(self) -> list[str]:
        return [f"{b.statement} (confiance={b.confidence:.2f}, preuves={b.evidence})" for b in self.beliefs.values()]

# ==========================================
# 4. MODÈLE PRÉDICTIF (Inférence active)
# ==========================================
@dataclass
class Prediction:
    expected_energy: float
    expected_danger: float
    confidence: float

class PredictiveModel:
    def predict(self, energy: float, danger: float, action: str) -> Prediction:
        if action == "fuir":
            expected_energy = max(0.0, energy - 0.08)
            expected_danger = max(0.0, danger - 0.25)
        elif action == "chercher":
            expected_energy = min(1.0, energy + 0.12)
            expected_danger = danger
        else:
            expected_energy = max(0.0, energy - 0.01)
            expected_danger = danger
        return Prediction(expected_energy=expected_energy, expected_danger=expected_danger, confidence=0.5)

    def error(self, prediction: Prediction, energy: float, danger: float) -> float:
        return (abs(prediction.expected_energy - energy) + abs(prediction.expected_danger - danger)) / 2.0

# ==========================================
# 5. MODÈLE DE SOI (Identité)
# ==========================================
@dataclass
class SelfModel:
    energy: float = 0.7
    danger: float = 0.0
    injury: float = 0.0
    fatigue: float = 0.0
    social_bonds: dict[int, float] = field(default_factory=dict)
    identity: str = "organisme_simule"

    def update(self, energy: float, danger: float, injury: float, fatigue: float) -> None:
        self.energy = energy
        self.danger = danger
        self.injury = injury
        self.fatigue = fatigue

    def status(self) -> dict:
        return {"energy": round(self.energy, 4), "danger": round(self.danger, 4), "identity": self.identity}

# ==========================================
# 6. MÉMOIRE ÉPISODIQUE
# ==========================================
@dataclass
class Episode:
    time: int
    observation: dict
    action: str
    consequence: dict
    surprise: float
    valence: float
    causes: list[str] = field(default_factory=list)

@dataclass
class EpisodicMemory:
    episodes: list[Episode] = field(default_factory=list)
    maximum: int = 500

    def remember(self, episode: Episode) -> None:
        self.episodes.append(episode)
        if len(self.episodes) > self.maximum: self.episodes = self.episodes[-self.maximum:]

# ==========================================
# 7. LE LANCEUR (Simulation de la Mouche)
# ==========================================
def choisir_action(energie: float, danger: float, idee: str | None) -> str:
    if idee == "danger_critique": return "fuir"
    if idee == "energie_faible": return "chercher"
    if danger > 0.6: return "fuir"
    if energie < 0.3: return "chercher"
    return "maintenir"

def main():
    print("==================================================")
    print("SIMULATION DE LA MOUCHE (AUTOPOÏÈSE)")
    print("==================================================")
    
    monde = World()
    memoire = EpisodicMemory()
    modele_predictif = PredictiveModel()
    modele_soi = SelfModel()
    metacognition = Metacognition()
    workspace = GlobalWorkspace()
    
    energie = 0.7
    danger = 0.0

    for temps in range(40):
        monde.step(temps)
        danger = monde.danger
        
        workspace.soumettre("danger_critique", danger, "perception", {"danger": danger})
        workspace.soumettre("energie_faible", 1.0 - energie, "modele_de_soi", {"energie": energie})
        
        idee = workspace.diffuser()
        nom_idee = idee.nom if idee is not None else None
        
        action = choisir_action(energie, danger, nom_idee)
        
        prediction = modele_predictif.predict(energie, danger, action)
        if action == "fuir":
            energie -= 0.08
            danger *= 0.88
        elif action == "chercher":
            energie += 0.05
        else:
            energie -= 0.01
            
        energie = max(0.0, min(1.0, energie))
        
        erreur = modele_predictif.error(prediction, energie, danger)
        
        episode = Episode(time=temps, observation={"energie": energie, "danger": danger}, action=action, consequence={"energie": energie, "danger": danger}, surprise=erreur, valence=-1.0 if danger > 0.6 else 0.5)
        memoire.remember(episode)
        
        modele_soi.update(energy=energie, danger=danger, injury=0.0, fatigue=max(0.0, 1.0 - energie))
        
        if nom_idee is not None:
            metacognition.revise(f"{action} répond à {nom_idee}", erreur)
        else:
            metacognition.revise(f"{action} en l'absence d'alerte", erreur)
            
        if temps % 5 == 0 or danger > 0.8:
            print(f"t={temps:2d} | idée={nom_idee} | action={action} | énergie={energie:.2f} | danger={danger:.2f}")

    print("\n===== RAPPORT FINAL DE LA MOUCHE =====")
    print(f"Souvenirs stockés : {len(memoire.episodes)}")
    print(f"Modèle de soi : {modele_soi.status()}")
    print("Croyances finales :")
    for croyance in metacognition.explain():
        print(" -", croyance)

if __name__ == "__main__":
    main()
