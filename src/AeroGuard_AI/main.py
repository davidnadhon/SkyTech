# main.py
# -------------------------------------------------------------
# Système ANAC - Menu Principal et Navigation Historique
# -------------------------------------------------------------

import os
import sys
import platform
import cv2
from datetime import datetime
from colorama import init, Fore, Back, Style

# Import des modules du projet
from detection.detection_video import DetecteurVideo
from utils.calcul_risque import CalculRisque
from utils.journalisation import Journalisation

# Initialisation des couleurs
init(autoreset=True)

# -------------------------------------------------------------
# Configuration Globale
# -------------------------------------------------------------
DOSSIER_VIDEOS = "videos"
DOSSIER_LOGS = "logs"
CHEMIN_MODELE = "models/yolov8s.pt"
PERIPHERIQUE_IA = "cpu"


# -------------------------------------------------------------
# Utilitaires d'Affichage
# -------------------------------------------------------------
def nettoyer_ecran():
    os.system('cls' if os.name == 'nt' else 'clear')


def appui_pour_continuer():
    input(f"\n{Fore.LIGHTBLACK_EX}Appuyez sur Entrée pour revenir...{Style.RESET_ALL}")


def afficher_entete_simple(titre):
    nettoyer_ecran()
    print(f"{Fore.BLUE}╔══════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.BLUE}║ {Fore.WHITE + Style.BRIGHT} {titre.center(64)} {Fore.BLUE}║")
    print(f"{Fore.BLUE}╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")


# -------------------------------------------------------------
# 1. Module Surveillance
# -------------------------------------------------------------
def lister_videos():
    if not os.path.exists(DOSSIER_VIDEOS): os.makedirs(DOSSIER_VIDEOS)
    return sorted([f for f in os.listdir(DOSSIER_VIDEOS) if f.lower().endswith(('.mp4', '.avi', '.mkv'))])


def surveiller_camera():
    videos = lister_videos()
    afficher_entete_simple("MODULE SURVEILLANCE")

    if not videos:
        print(f"{Fore.RED}❌ Aucune vidéo trouvée dans le dossier '{DOSSIER_VIDEOS}'.{Style.RESET_ALL}")
        appui_pour_continuer()
        return

    print("Veuillez sélectionner une caméra pour lancer l'analyse :\n")
    for i, vid in enumerate(videos, 1):
        print(f" {Fore.MAGENTA}[{i}]{Style.RESET_ALL} {vid}")
    print(f"\n {Fore.RED}[0]{Style.RESET_ALL} Retour Menu Principal")

    choix = input(f"\n{Fore.YELLOW}Votre choix > {Style.RESET_ALL}").strip()

    if choix == "0" or not choix.isdigit(): return

    idx = int(choix) - 1
    if 0 <= idx < len(videos):
        nom_fichier = videos[idx]
        chemin_video = os.path.join(DOSSIER_VIDEOS, nom_fichier)
        # Le nom de la zone sera le nom du fichier sans extension (ex: "Entree_Nord")
        nom_zone = os.path.splitext(nom_fichier)[0]

        print(f"\n{Fore.CYAN}Initialisation de la zone : {nom_zone}...{Style.RESET_ALL}")

        try:
            # Création des instances
            risque = CalculRisque()
            journal = Journalisation(DOSSIER_LOGS)
            detecteur = DetecteurVideo(CHEMIN_MODELE, risque, journal, PERIPHERIQUE_IA)

            detecteur.analyser_video(nom_zone, chemin_video)
        except Exception as e:
            print(f"{Fore.RED}Erreur critique lors de l'exécution : {e}{Style.RESET_ALL}")
            appui_pour_continuer()


# -------------------------------------------------------------
# 2. Module Analyse des Logs (Navigation Date -> Zone -> Résumé)
# -------------------------------------------------------------

def analyser_fichier_zone(chemin_fichier_log, nom_zone, date_selectionnee):
    """
    Lit un fichier log spécifique et affiche un résumé statistique.
    """
    afficher_entete_simple(f"RAPPORT : {nom_zone.upper()}")
    print(f"Date du rapport : {Fore.CYAN}{date_selectionnee}{Style.RESET_ALL}")
    print(f"Fichier source  : {os.path.basename(chemin_fichier_log)}\n")

    nb_total = 0
    nb_eleve = 0
    nb_moyen = 0
    nb_faible = 0
    derniers_incidents = []

    try:
        with open(chemin_fichier_log, "r", encoding="utf-8") as f:
            lignes = f.readlines()
            nb_total = len(lignes)

            for ligne in lignes:
                if "NIVEAU=ÉLEVÉ" in ligne:
                    nb_eleve += 1
                elif "NIVEAU=MOYEN" in ligne:
                    nb_moyen += 1
                else:
                    nb_faible += 1

            # On garde les 5 derniers pour l'affichage
            derniers_incidents = lignes[-5:] if nb_total > 5 else lignes

    except Exception as e:
        print(f"{Fore.RED}Erreur de lecture du fichier : {e}{Style.RESET_ALL}")
        appui_pour_continuer()
        return

    # Affichage du Résumé
    print(f"{Back.WHITE}{Fore.BLACK} STATISTIQUES DE LA ZONE {Style.RESET_ALL}\n")
    print(f"📊 Total Incidents : {Style.BRIGHT}{nb_total}{Style.RESET_ALL}")
    print(f"🔴 Risques ÉLEVÉS  : {Fore.RED}{nb_eleve}{Style.RESET_ALL}")
    print(f"🟠 Risques MOYENS  : {Fore.YELLOW}{nb_moyen}{Style.RESET_ALL}")
    print(f"🟢 Risques FAIBLES : {Fore.GREEN}{nb_faible}{Style.RESET_ALL}")

    print(f"\n{Fore.LIGHTBLACK_EX}--- 5 DERNIERS INCIDENTS ENREGISTRÉS ---{Style.RESET_ALL}")
    if not derniers_incidents:
        print("Aucun incident.")
    else:
        for inc in derniers_incidents:
            # Nettoyage visuel de la ligne
            print(inc.strip())

    # Menu contextuel
    print(f"\n{Fore.YELLOW}Options :{Style.RESET_ALL}")
    print("1. Voir tout le fichier brut")
    print("0. Retour au choix des zones")

    choix = input("\nVotre choix > ")
    if choix == "1":
        print("\n--- DÉBUT DU FICHIER ---")
        try:
            with open(chemin_fichier_log, "r", encoding="utf-8") as f:
                print(f.read())
        except:
            pass
        print("--- FIN DU FICHIER ---")
        appui_pour_continuer()


def choisir_zone_dans_date(date_dossier):
    """
    Liste les fichiers (zones) dans un dossier de date spécifique.
    """
    chemin_dossier = os.path.join(DOSSIER_LOGS, date_dossier)

    while True:
        afficher_entete_simple(f"ZONES DU {date_dossier}")

        if not os.path.exists(chemin_dossier):
            print(f"{Fore.RED}Le dossier {date_dossier} n'existe plus.{Style.RESET_ALL}")
            appui_pour_continuer()
            return

        # On ne prend que les fichiers .log
        fichiers = [f for f in os.listdir(chemin_dossier) if f.endswith(".log")]

        if not fichiers:
            print(f"{Fore.YELLOW}Aucune zone enregistrée pour cette date.{Style.RESET_ALL}")
            appui_pour_continuer()
            return

        print("Sélectionnez une zone à analyser :\n")
        for i, fichier in enumerate(fichiers, 1):
            # On enlève l'extension .log pour l'affichage
            nom_zone = fichier.replace(".log", "")
            print(f" {Fore.CYAN}[{i}]{Style.RESET_ALL} {nom_zone}")

        print(f"\n {Fore.RED}[0]{Style.RESET_ALL} Retour aux dates")

        choix = input(f"\n{Fore.YELLOW}Votre choix > {Style.RESET_ALL}").strip()

        if choix == "0":
            return  # On remonte d'un niveau

        if choix.isdigit():
            idx = int(choix) - 1
            if 0 <= idx < len(fichiers):
                fichier_choisi = fichiers[idx]
                chemin_complet = os.path.join(chemin_dossier, fichier_choisi)
                # Appel de la fonction de résumé
                analyser_fichier_zone(chemin_complet, fichier_choisi.replace(".log", ""), date_dossier)


def navigation_historique():
    """
    Premier niveau : Liste les dossiers (Dates)
    """
    while True:
        afficher_entete_simple("ARCHIVES ET HISTORIQUE")

        if not os.path.exists(DOSSIER_LOGS):
            print("Aucun dossier de logs trouvé.")
            appui_pour_continuer()
            return

        # Liste des dossiers (Dates), triée par date décroissante (le plus récent en haut)
        dossiers_dates = [d for d in os.listdir(DOSSIER_LOGS) if os.path.isdir(os.path.join(DOSSIER_LOGS, d))]
        dossiers_dates.sort(reverse=True)

        if not dossiers_dates:
            print(f"{Fore.YELLOW}Aucune archive disponible.{Style.RESET_ALL}")
            appui_pour_continuer()
            return

        print("Sélectionnez une date :\n")
        for i, date_dossier in enumerate(dossiers_dates, 1):
            print(f" {Fore.GREEN}[{i}]{Style.RESET_ALL} {date_dossier}")

        print(f"\n {Fore.RED}[0]{Style.RESET_ALL} Retour Menu Principal")

        choix = input(f"\n{Fore.YELLOW}Votre choix > {Style.RESET_ALL}").strip()

        if choix == "0":
            return

        if choix.isdigit():
            idx = int(choix) - 1
            if 0 <= idx < len(dossiers_dates):
                date_selectionnee = dossiers_dates[idx]
                # On descend dans le dossier choisi
                choisir_zone_dans_date(date_selectionnee)


def acces_rapide_aujourdhui():
    """Raccourci pour aller directement dans le dossier du jour."""
    date_jour = datetime.now().strftime("%Y-%m-%d")
    chemin = os.path.join(DOSSIER_LOGS, date_jour)

    if os.path.exists(chemin):
        choisir_zone_dans_date(date_jour)
    else:
        print(f"\n{Fore.YELLOW}Aucune donnée enregistrée pour aujourd'hui ({date_jour}).{Style.RESET_ALL}")
        print("Lancez une surveillance pour créer des logs.")
        appui_pour_continuer()


# -------------------------------------------------------------
# 3. Informations Système
# -------------------------------------------------------------
def infos_systeme():
    afficher_entete_simple("INFORMATIONS SYSTÈME")
    print(f"OS           : {platform.system()} {platform.release()}")
    print(f"Python       : {sys.version.split()[0]}")
    print(f"OpenCV       : {cv2.__version__}")
    print(f"Modèle IA    : {CHEMIN_MODELE}")
    print(f"Dossier Logs : {os.path.abspath(DOSSIER_LOGS)}")
    print(f"\n{Fore.BLUE}Développé pour le projet ANAC{Style.RESET_ALL}")
    appui_pour_continuer()


# -------------------------------------------------------------
# MENU PRINCIPAL
# -------------------------------------------------------------
def main():
    while True:
        afficher_entete_simple("CENTRE DE CONTRÔLE ANAC")

        # Dashboard minimaliste intégré au menu
        date_str = datetime.now().strftime("%d/%m/%Y")
        print(f"{Fore.CYAN}📅 Date : {date_str}  |  🚀 Statut : PRÊT{Style.RESET_ALL}")
        print("──────────────────────────────────────────────────────────────────\n")

        print(f" {Fore.MAGENTA}1️⃣   Surveiller une caméra (Zone){Style.RESET_ALL}")
        print(f" {Fore.GREEN}2️⃣   Rapports d'aujourd'hui (Accès Rapide){Style.RESET_ALL}")
        print(f" {Fore.BLUE}3️⃣   Explorer les Archives (Par Date & Zone){Style.RESET_ALL}")
        print(f" {Fore.WHITE}4️⃣   Informations Système{Style.RESET_ALL}")
        print(" ─────────────────────────────────")
        print(f" {Fore.RED}0️⃣   Quitter le système{Style.RESET_ALL}")

        choix = input(f"\n{Fore.BLUE}ANAC > {Style.RESET_ALL}").strip()

        if choix == "1":
            surveiller_camera()
        elif choix == "2":
            acces_rapide_aujourdhui()
        elif choix == "3":
            navigation_historique()
        elif choix == "4":
            infos_systeme()
        elif choix == "0":
            print(f"\n{Fore.RED}Fermeture du système... À bientôt.{Style.RESET_ALL}")
            break


if __name__ == "__main__":
    main()