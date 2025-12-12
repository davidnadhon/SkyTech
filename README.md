# 📘 AeroGuard AI & SheJoy AI — Projet SkyTech
![Version](https://img.shields.io/badge/Version-1.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11-yellow.svg)
![Status](https://img.shields.io/badge/Status-Suite_Unifiée-orange.svg)

> **Projet d'Innovation - Concours ANAC 2025**
> *Une approche globale unifiant la sécurité au sol (Tarmac) et la sécurité en vol (Pilotes).*

---

## 🌍 Vision du Projet

La sécurité aérienne ne se limite pas à une seule zone. Ce dépôt contient **deux solutions d'Intelligence Artificielle** distinctes mais complémentaires, développées pour couvrir l'ensemble de la chaîne de risque.

| Module | Nom | Cible | Technologie |
| :--- | :--- | :--- | :--- |
| **1️⃣ SOL** | **AeroGuard AI** | Tarmac & Pistes | Vision par Ordinateur (YOLOv8) |
| **2️⃣ VOL** | **SheJoy AI** | Équipages & Pilotes | Machine Learning (Random Forest) |

---

## ✈️ Module 1 : AeroGuard AI (Surveillance Sol)
> *Solution de Vision par Ordinateur pour la sécurisation automatisée des zones critiques.*

### 🔴 Le Problème
La surveillance du tarmac repose sur la vigilance humaine. Un agent ne peut pas surveiller 50 écrans simultanément 24h/24 sans fatigue, créant un risque élevé d'intrusions non détectées.

### 🟢 La Solution
Un système autonome qui **comprend** ce qu'il voit :
1.  **Détection IA** : Identifie les objets en temps réel (Personnes, Camions, Animaux).
2.  **Analyse de Risque** : Décide instantanément si l'objet est autorisé ou dangereux selon la zone.
3.  **Traçabilité** : Archivage automatique et infalsifiable des incidents (Logs/Preuves).

### Fonctionnalités Principales

#### 1. Surveillance Temps Réel (HUD)
Une interface "Tête Haute" s'affiche directement sur le flux vidéo.
*   🟢 **Vert** : Situation Normale.
*   🔴 **Rouge** : Alerte Intrusion (Enregistrement déclenché + Message d'alerte).

#### 2. Journalisation Intelligente
Les incidents sont triés automatiquement pour faciliter les enquêtes :
*   📂 Un dossier par **Date** (ex: `logs/2025-12-10/`).
*   📄 Un fichier par **Zone/Caméra** (ex: `Piste_Nord.log`).

#### 3. Tableau de Bord de Commandement
Un menu interactif permet aux superviseurs de :
*   Lancer la surveillance sur une caméra spécifique.
*   Consulter le résumé des incidents de la journée.
*   Accéder aux archives historiques.

---

## 👨‍✈️ Module 2 : SheJoy AI (Prédiction Fatigue)
> *Système prédictif pour sécuriser les vols en anticipant la fatigue humaine.*

### 🔴 Le Problème
En Afrique de l'Ouest plus précisement au Togo, la sécurité des passagers est une priorité. Cependant, une faille critique subsiste : **la fatigue des pilotes**. Bien que les temps de repos légaux soient respectés, ils ne garantissent pas physiologiquement qu'un pilote soit apte à voler (stress, biorythme, conditions personnelles).

### 🟢 La Solution
Nous répondons à cette question : *"Comment assurer la sécurité de centaines de passagers face au risque humain ?"*
**SheJoy AI** est une solution prédictive qui analyse des données spécifiques (historique, rythme circadien, planning) pour déterminer **à l'avance** si un pilote est fatigué. Si un risque est détecté, le système propose automatiquement un remplacement.

### ✨ 2. Fonctionnalités Principales

Notre prototype couvre 4 axes majeurs :

*   **🧠 Scoring IA Prédictif :** Utilisation d'un modèle *Random Forest Regressor* pour calculer un score de fatigue (%) précis pour chaque pilote.
*   **📅 Analyse Multi-Horizons :** Capacité d'analyser les équipages en temps réel (J-0) ou de prévoir les risques futurs (J-3, J-7).
*   **🔄 Décision Opérationnelle Automatisée :** Suggestion intelligente de pilotes remplaçants "Aptes" en cas d'alerte critique.
*   **🛡️ Traçabilité (Logs) :** Enregistrement automatique de toutes les analyses et décisions dans un journal d'audit sécurisé.

---


---

## 🏗️ Architecture du Dépôt

Le projet est organisé de manière modulaire dans le dossier `src/`. Chaque projet est indépendant.

```text
SkyTech_Project/
│
├── requirements.txt         <-- Dépendances pour LES DEUX projets
│
└── src/                     <-- Code Source
    │
    ├── AeroGuard_AI/           <-- DOSSIER PROJET 1
    │   ├── main.py          <-- Lanceur AeroGuard
    │   ├── detection/
    │   └── utils/
    │
    └── SehJoy_AI/              <-- DOSSIER PROJET 2
        ├── application_CLI.py <-- Lanceur SheJoy
        ├── data/
        └── models/ 

```
## 💻 Guide d'Installation (Commun)

Suivez ces étapes pour préparer l'environnement technique unifié pour les deux projets.

### 1️⃣ Prérequis
*   Avoir **Python 3.10 ou 3.11** installé sur votre machine.
*   *Sur Windows :* Avoir coché l'option **"Add Python to PATH"** lors de l'installation.

---

### 2️⃣ Création de l'environnement virtuel (VITAL)

Pour éviter les conflits de versions, nous utilisons un environnement virtuel unique pour toute la suite.

**🪟 Sur Windows (PowerShell) :**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 🍎🐧 Sur Mac / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```
✅ Vérification : Vous devez voir (venv) apparaître au début de votre ligne de commande.

### 3️⃣ Installation des dépendances

Installez les librairies nécessaires pour AeroGuard (Vision) et SheJoy (Data) :

```bash
pip install -r requirements.txt
```

### 🚀 Guide de Lancement

Une fois l'installation terminée, choisissez le module à lancer :

```bash
🎥 Lancer AeroGuard AI (Surveillance Sol)
cd src/AeroGuard_AI
python main.py
```

👉 L’interface de surveillance vidéo s’ouvrira automatiquement.

### 🧠 Lancer SheJoy AI (Prédiction Fatigue Pilote)

```bash
cd src/SheJoy_AI
python application_CLI.py
```

👉 Le menu de prédiction de fatigue s’affichera dans la console.

### 👥 Équipe Projet SkyTech

Développé pour l’innovation aéronautique au Togo.

*   YATA Eric (CG), Ingénieur Réseaux, Systèmes et Sécurité en Formation
*   POZOU Ewaba Emmanuel, Ingénieur Cybersécurité en Formation & DevOps
*   ALIKIZAN Joyce, Ingénieur Cybersécurité en Formation
*   NADHON Kokou David, Ingénieur Cybersécurité en Formation
*   GNANSSA Lidaw Luc, Ingénieur Réseaux, Systèmes et Sécurité en Formation