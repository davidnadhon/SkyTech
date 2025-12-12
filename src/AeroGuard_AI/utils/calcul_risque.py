# utils/calcul_risque.py
# -------------------------------------------------------------
# Calcule le niveau de risque en fonction des objets détectés.
# -------------------------------------------------------------

class CalculRisque:
    def __init__(self):
        # dictionnaire du niveau de danger des objets
        self.risque_objet = {
            "person": 4,
            "dog": 3,
            "cat": 2,
            "bird": 3,
            "car": 2,
            "truck": 4,
            "motorcycle": 2,
            "suitcase": 1,
            "backpack": 1,
            "handbag": 1
        }

    def calculer_risque(self, objets):
        """
        Retourne score total + niveau : FAIBLE, MOYEN, ÉLEVÉ
        """
        score = 0
        for obj in objets:
            score += self.risque_objet.get(obj, 0)

        if score >= 6:
            return score, "ÉLEVÉ"
        elif score >= 3:
            return score, "MOYEN"
        else:
            return score, "FAIBLE"

    def est_dangereux(self, objet):
        """"
        Retourne True si objet est dangereux
        """
        return objet in self.risque_objet
