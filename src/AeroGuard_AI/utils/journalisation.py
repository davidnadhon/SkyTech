# utils/journalisation.py
# -------------------------------------------------------------
# Gestion des logs : Structure hiérarchique (Date -> Zone)
# -------------------------------------------------------------

import os
from datetime import datetime


class Journalisation:
    def __init__(self, dossier_racine="logs"):
        """
        Initialise le gestionnaire de logs.
        :param dossier_racine: Le dossier principal (ex: 'logs')
        """
        self.dossier_racine = dossier_racine

        # On s'assure que le dossier principal existe
        if not os.path.exists(self.dossier_racine):
            os.makedirs(self.dossier_racine)

    def _preparer_dossier_du_jour(self):
        """
        Crée et retourne le chemin du dossier pour la date actuelle.
        Exemple : logs/2025-12-09/
        """
        date_jour = datetime.now().strftime("%Y-%m-%d")
        chemin_dossier_jour = os.path.join(self.dossier_racine, date_jour)

        if not os.path.exists(chemin_dossier_jour):
            os.makedirs(chemin_dossier_jour)

        return chemin_dossier_jour

    def enregistrer(self, nom_zone, objets, score, niveau):
        """
        Enregistre une alerte dans le fichier spécifique de la zone (caméra).
        Le fichier est automatiquement placé dans le dossier du jour.
        """
        try:
            dossier_jour = self._preparer_dossier_du_jour()

            # Nettoyage du nom de la zone pour éviter les erreurs de système de fichiers
            # Ex: "Caméra Nord" devient "Camera_Nord.log"
            nom_fichier_propre = nom_zone.replace(" ", "_").replace("/", "-") + ".log"
            chemin_fichier = os.path.join(dossier_jour, nom_fichier_propre)

            heure_actuelle = datetime.now().strftime("%H:%M:%S")

            # Format lisible et facile à parser
            ligne_log = (
                f"[{heure_actuelle}] "
                f"ZONE={nom_zone} | "
                f"NIVEAU={niveau} | "
                f"SCORE={score} | "
                f"OBJETS={objets}\n"
            )

            with open(chemin_fichier, "a", encoding="utf-8") as f:
                f.write(ligne_log)

        except Exception as e:
            print(f"[ERREUR LOGS] Impossible d'écrire : {e}")

    def afficher_console(self, nom_zone, objets, score, niveau):
        """Affiche l'alerte dans la console pour le debug."""
        print(f" >> [LOG] {nom_zone} : {objets} (Niveau {niveau})")