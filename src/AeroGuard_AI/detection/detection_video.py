# detection/detection_video.py
# -------------------------------------------------------------
# Analyse vidéo avec YOLO + affichage HUD dynamique + alertes
# -------------------------------------------------------------

import cv2
from ultralytics import YOLO


class DetecteurVideo:
    # Constantes de couleurs (Format BGR pour OpenCV)

    COULEURS_OBJETS = {
        "person": (0, 0, 255),  # Rouge
        "car": (0, 255, 0),  # Vert
        "truck": (0, 165, 255),  # Orange
        "dog": (255, 0, 0),  # Bleu
        "cat": (255, 0, 255),  # Rose
        "bird": (0, 255, 255),  # Jaune
    }

    COULEURS_RISQUE = {
        "FAIBLE": (0, 180, 0),  # Vert foncé
        "MOYEN": (0, 140, 255),  # Orange vif
        "ÉLEVÉ": (0, 0, 200)  # Rouge vif
    }

    def __init__(self, chemin_modele, calculateur_risque, journal, peripherique="cpu"):
        """
        Initialise le détecteur avec le modèle YOLO et les gestionnaires de risques/logs.
        """
        print(f"[INIT] Chargement du modèle YOLO : {chemin_modele}")
        self.modele = YOLO(chemin_modele)
        self.risque = calculateur_risque
        self.journal = journal
        self.peripherique = peripherique

    def _dessiner_hud(self, frame, niveau, nombre_objets):
        """
        Méthode privée pour dessiner le bandeau d'alerte en haut de l'image.
        S'adapte dynamiquement à la largeur de l'image.
        """
        hauteur_img, largeur_img = frame.shape[:2]

        # Hauteur du bandeau (fixe, ex: 60 pixels)
        hauteur_bandeau = 60

        # Récupération de la couleur de fond selon le niveau
        couleur_fond = self.COULEURS_RISQUE.get(niveau, (50, 50, 50))

        # 1. Dessiner le rectangle plein (Fond coloré)
        # Coordonnées : Coin haut-gauche (0,0) -> Coin bas-droit (Largeur Image, 60px)
        cv2.rectangle(frame, (0, 0), (largeur_img, hauteur_bandeau), couleur_fond, -1)

        # 2. Préparer le texte
        texte = f"NIVEAU: {niveau}  |  DANGER: {nombre_objets} OBJET(S) DETECTE(S)"

        # 3. Centrer le texte (Calcul de la taille du texte pour le placer au milieu)
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.8
        thickness = 2
        (taille_texte_w, taille_texte_h), _ = cv2.getTextSize(texte, font, scale, thickness)

        pos_x = (largeur_img - taille_texte_w) // 2
        pos_y = (hauteur_bandeau + taille_texte_h) // 2 - 2  # Petit ajustement vertical

        # 4. Écrire le texte en BLANC
        cv2.putText(frame, texte, (pos_x, pos_y), font, scale, (255, 255, 255), thickness)

    def analyser_video(self, camera_nom, chemin_video):
        """
        Boucle principale de lecture et de traitement vidéo.
        """
        flux = cv2.VideoCapture(chemin_video)

        if not flux.isOpened():
            print(f"[ERREUR] Impossible d'ouvrir la vidéo : {chemin_video}")
            return

        print(f"[INFO] Démarrage analyse caméra : {camera_nom}")
        print("[INFO] Appuyez sur 'q' pour quitter l'affichage.")

        while True:
            succes, frame = flux.read()
            if not succes:
                print("[INFO] Fin du flux vidéo.")
                break

            # --- 1. DÉTECTION IA ---
            resultats = self.modele(frame, verbose=False, device=self.peripherique)[0]
            objets_dangereux = []

            # --- 2. DESSIN DES BOITES (Objets) ---
            for box in resultats.boxes:
                classe_id = int(box.cls)
                nom_objet = self.modele.names[classe_id]
                confiance = float(box.conf[0])

                # Filtrage confiance faible
                if confiance < 0.4:
                    continue

                # Coordonnées
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Couleur objet
                couleur = self.COULEURS_OBJETS.get(nom_objet, (200, 200, 200))

                # Dessin Boite + Label
                cv2.rectangle(frame, (x1, y1), (x2, y2), couleur, 2)
                cv2.putText(frame, f"{nom_objet}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, couleur, 2)

                # Vérification risque
                if self.risque.est_dangereux(nom_objet):
                    objets_dangereux.append(nom_objet)

            # --- 3. LOGIQUE MÉTIER (Calcul Risque) ---
            score, niveau = self.risque.calculer_risque(objets_dangereux)

            # --- 4. AFFICHAGE HUD (Interface Propre) ---
            self._dessiner_hud(frame, niveau, len(objets_dangereux))

            # --- 5. ENREGISTREMENT LOGS (Si nécessaire) ---
            if niveau in ["MOYEN", "ÉLEVÉ"] and objets_dangereux:
                # On logue uniquement si c'est pertinent pour éviter de spammer le fichier
                self.journal.enregistrer(camera_nom, objets_dangereux, score, niveau)

            # --- 6. RENDU ---
            cv2.imshow(f"ANAC MONITORING - {camera_nom}", frame)

            # Quitter avec 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        flux.release()
        cv2.destroyAllWindows()