import pandas as pd
import joblib
import os
import datetime
from colorama import Fore, Style, init

#initialisation de colorama pour les sorties de couleurs
init(autoreset=True)

#Les paramètres à prendre en compte
SEUIL_APTITUDE_PCT = 60
JOURNAL_FILE = "journal.csv"


#Initialisation du modele RandomForest entrainé
try:
    modele = joblib.load("models\modele_fatigue.pkl")
except Exception as e:
    print(f"Erreur lors du chargement du modèle : {e}")
    exit()

#Donnees à charger pour chaque options
donnees_jour = pd.DataFrame()
donnees_j3 = pd.DataFrame()
donnees_j7 = pd.DataFrame()



def log_action(type_action, details=""):
    """Fonction mise en place pour répertorier les logs de tout ce qui sera fait dans le programme"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {"date": now, "action": type_action, "details": details}
    
    if os.path.exists(JOURNAL_FILE):
        df_journal = pd.read_csv(JOURNAL_FILE)
        df_journal = pd.concat([df_journal, pd.DataFrame([entry])], ignore_index=True)
    else:
        df_journal = pd.DataFrame([entry])
    
    df_journal.to_csv(JOURNAL_FILE, index=False)


def menu_journal():
    """Fonction pour le journal"""
    if os.path.exists(JOURNAL_FILE):
        df_journal = pd.read_csv(JOURNAL_FILE)
        if df_journal.empty:
            print("Aucun journal disponible.")
            return
        print("\n=== Journaux & Historique ===")
        for _, row in df_journal.iterrows():
            print(f"[{row['date']}] {row['action']} -> {row['details']}")
    else:
        print("Aucun journal disponible.")


def importer_csv_horizon(horizon_jours):
    """Fonction pour importer toutes les données si nécessaire"""
    global donnees_jour, donnees_j3, donnees_j7
    fichiers = input("Entrez le(s) chemin(s) CSV séparés par une virgule : ").split(",")
    dfs = []
    for f in fichiers:
        f = f.strip()
        if os.path.exists(f):
            df = pd.read_csv(f)
            dfs.append(df)
        else:
            print(f"Fichier introuvable : {f}")
    if dfs:
        df_concat = pd.concat(dfs, ignore_index=True)
        if horizon_jours==0:
            donnees_jour = df_concat
        elif horizon_jours==3:
            donnees_j3 = df_concat
        elif horizon_jours==7:
            donnees_j7 = df_concat
        print(f"✅ Données du vol chargées pour l’horizon {horizon_jours} jours.")
        log_action("Import CSV", f"Horizon {horizon_jours} jours, fichiers : {', '.join(fichiers)}")
    else:
        print("❌ Aucun fichier valide chargé.")


def menu_importation():
    """Sous-lenu pour charger les données des vols pour une analyse plutard"""
    while True:
        print("\n=== Importation / Synchronisation des données ===")
        print("1. Charger données vol du jour")
        print("2. Charger données vol dans 3 jours")
        print("3. Charger données vol dans 7 jours")
        print("4. Retour")
        choix = input("Choix : ")
        if choix=="1":
            importer_csv_horizon(0)
        elif choix=="2":
            importer_csv_horizon(3)
        elif choix=="3":
            importer_csv_horizon(7)
        elif choix=="4":
            break
        else:
            print("Choix invalide.")


def get_donnees_selon_horizon(horizon_jours):
    """Fonction pour charger les données selons le jour ou l'option choisi"""
    if horizon_jours == 0:
        df = donnees_jour
        label = "du jour"
    elif horizon_jours == 3:
        df = donnees_j3
        label = "dans 3 jours"
    elif horizon_jours == 7:
        df = donnees_j7
        label = "dans 7 jours"
    else:
        return None

    if df.empty:
        print(f"⚠️ Données du vol {label} non chargées. Veuillez importer le CSV.")
        importer_csv_horizon(horizon_jours)
        df = get_donnees_selon_horizon(horizon_jours)
    return df



def afficher_tableau(df):
    """Fonction pour afficher un tableau avec des couleurs via la bibliothèque colorama"""
    print("\n{:<10} {:<20} {:<10} {:<15} {:<10}".format(
        "ID Pilote", "Nom Pilote", "Vol", "Fatigue (%)", "Aptitude"
    ))
    print("-"*70)
    for _, row in df.iterrows():
        score = f"{row['score_fatigue']:.0f} %"
        if row['aptitude']=="Apt":
            aptitude_col = Fore.GREEN + row['aptitude'] + Style.RESET_ALL
        else:
            aptitude_col = Fore.RED + row['aptitude'] + " ⚠️" + Style.RESET_ALL
        print("{:<10} {:<20} {:<10} {:<15} {:<10}".format(
            row['id_pilote'], row['nom_pilote'], row['id_vol'], score, aptitude_col
        ))


def analyse_fatigue(horizon_jours):
    """Fonction pour analyser et prédire le risque de fatigue"""
    df = get_donnees_selon_horizon(horizon_jours)
    if df is None or df.empty:
        return
    df['score_fatigue'] = modele.predict(df) * 100
    df['aptitude'] = df['score_fatigue'].apply(lambda x: "Apt" if x < SEUIL_APTITUDE_PCT else "Non apt")
    afficher_tableau(df)
    log_action("Analyse fatigue", f"Horizon {horizon_jours} jours, {len(df)} pilotes analysés")
    return df


def decision_remplacement(remplacer_type='pilote'):
    """Fonction pour automatiser la décision de remplacement si nécessaire"""
    df_analyse = analyse_fatigue(0)
    if df_analyse is None:
        return
    non_aptes = df_analyse[df_analyse['aptitude']=='Non apt']
    if non_aptes.empty:
        print("✅ Aucun pilote non apte pour ce vol.")
        return

    remplaçants = donnees_jour[donnees_jour['id_pilote'].isin(
        df_analyse[df_analyse['aptitude']=='Apt']['id_pilote'])]
    
    if remplacer_type=='pilote':
        details = []
        for _, row in non_aptes.iterrows():
            suggestion = remplaçants.sample(1).iloc[0]
            details.append(f"{row['nom_pilote']}→{suggestion['nom_pilote']}")
            print(f"{Fore.RED}{row['nom_pilote']}{Style.RESET_ALL} ({row['id_vol']}) → Remplacé par {Fore.GREEN}{suggestion['nom_pilote']}{Style.RESET_ALL}")
        log_action("Remplacement pilote", "; ".join(details))
    else:
        details = []
        vols = non_aptes['id_vol'].unique()
        for vol in vols:
            pilotes_vol = non_aptes[non_aptes['id_vol']==vol]
            print(f"\nVol {vol} :")
            for _, row in pilotes_vol.iterrows():
                suggestion = remplaçants.sample(1).iloc[0]
                details.append(f"{row['nom_pilote']}→{suggestion['nom_pilote']}")
                print(f"{Fore.RED}{row['nom_pilote']}{Style.RESET_ALL} → Remplacé par {Fore.GREEN}{suggestion['nom_pilote']}{Style.RESET_ALL}")
        log_action("Remplacement équipage", "; ".join(details))



def menu_analyse_fatigue():
    """Fonction pour afficher le sous-menu contenu dans Analyse fatigue"""
    while True:
        print("\n=== Analyse fatigue des pilotes ===")
        print("1. Pilotes du jour")
        print("2. Pilotes dans 3 jours")
        print("3. Pilotes dans 7 jours")
        print("4. Retour")
        choix = input("Choix : ")
        if choix=="1":
            analyse_fatigue(0)
        elif choix=="2":
            analyse_fatigue(3)
        elif choix=="3":
            analyse_fatigue(7)
        elif choix=="4":
            break
        else:
            print("Choix invalide.")

def menu_decisions_operationnelles():
    """Fonction pour afficher le sous-menu dans Décison opérationnelle"""
    while True:
        print("\n=== Décisions opérationnelles ===")
        print("1. Remplacer un pilote fatigué")
        print("2. Remplacer tout un équipage")
        print("3. Retour")
        choix = input("Choix : ")
        if choix=="1":
            decision_remplacement('pilote')
        elif choix=="2":
            decision_remplacement('equipage')
        elif choix=="3":
            break
        else:
            print("Choix invalide.")

def menu_option_1():
    """Fonction pour affichier le sous menu de Analyse fatigue & décision opérationnelle"""
    while True:
        print("\n=== Analyse fatigue & décision opérationnelle ===")
        print("1. Analyse fatigue des pilotes")
        print("2. Décisions opérationnelles")
        print("3. Retour au menu principal")
        choix = input("Choix : ")
        if choix=="1":
            menu_analyse_fatigue()
        elif choix=="2":
            menu_decisions_operationnelles()
        elif choix=="3":
            break
        else:
            print("Choix invalide.")


def menu_principal():
    """Fonction pour affichier le menu principal"""
    while True:
        print("\n"+"="*57)
        print("   SYSTÈME PREDICTIF DE FATIGUE & GESTION DES ÉQUIPAGES  ")
        print("                     OCC DUTY MANAGER")
        print("="*57)
        print("1. Analyse fatigue & décision opérationnelle")
        print("2. Gestion des équipages (en dev)")
        print("3. Importation / Synchronisation des données")
        print("4. Modèle prédictif & Configuration système (en dev)")
        print("5. Journaux & Historique")
        print("6. Quitter")
        print("-"*57)
        choix = input("Choisissez une option : ")
        if choix=="1":
            menu_option_1()
        elif choix=="2":
            print("Fonctionnalité en développement...")
        elif choix=="3":
            menu_importation()
        elif choix=="4":
            print("Fonctionnalité en développement...")
        elif choix=="5":
            menu_journal()
        elif choix=="6":
            print("Au revoir !")
            break
        else:
            print("Choix invalide.")


#Fonction pour lancer le programme
if __name__ == "__main__":
    menu_principal()
