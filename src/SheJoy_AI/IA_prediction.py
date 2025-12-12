from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split # Import pour le split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score # Import pour les métriques
import pandas as pd
import joblib
import numpy as np

# 1. Chargement des données
try:
    df = pd.read_csv("Modele d'entrainement/entrainement.csv")
    print(f"Données chargées avec succès. Taille totale : {df.shape}")
except FileNotFoundError:
    print("Erreur : Le fichier CSV est introuvable.")
    exit()

X = df.drop("score_fatigue", axis=1)
y = df["score_fatigue"]

#Séparation des données (Split Train/Test)
# test_size=0.2 signifie que 20% des données serviront au test, 80% à l'entraînement
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Données d'entraînement : {X_train.shape[0]} lignes")
print(f"Données de test : {X_test.shape[0]} lignes")

# 3. Définition des colonnes
colonnes_numeriques = [
    "heure_debut_service", "heure_fin_service", "duree_vol",
    "repos_avant_service", "nombre_etapes",
    "jours_consecutifs_travail", "heures_48h", "heures_7j",
    "fuseaux_traverses",
    "experience_annees", "age_pilote",
    "duree_service_mensuelle_moyenne", "rapports_fatigue_90j",
    "auto_evaluation"
]

colonnes_categorielles = [
    "type_appareil", "equipage_augmente", "type_vol",
    "est_service_nuit", "voyage_est", "debut_fenetre_sommeil",
    "fin_fenetre_sommeil"
]

# Préprocesseur
preprocesseur = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), colonnes_numeriques),
        ("cat", OneHotEncoder(handle_unknown="ignore"), colonnes_categorielles)
    ]
)

# Modèle RandomForest
modele = RandomForestRegressor(
    n_estimators=600,
    max_depth=30,
    min_samples_split=4,
    min_samples_leaf=2,
    max_features="sqrt",
    bootstrap=True,
    n_jobs=-1,
    random_state=42
)

# Pipeline complet
pipeline = Pipeline([
    ("preprocessing", preprocesseur),
    ("model", modele)
])

# Entraînement (uniquement sur X_train et y_train)
print("\nDébut de l'entraînement...")
pipeline.fit(X_train, y_train)
print("Entraînement terminé.")

# Évaluation du modèle (sur X_test et y_test)
print("\n--- Résultats de l'évaluation ---")
y_pred = pipeline.predict(X_test)

# Calcul des métriques
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"MAE (Erreur Moyenne Absolue) : {mae:.4f}")
print(f"RMSE (Racine de l'Erreur Quadratique Moyenne) : {rmse:.4f}")
print(f"R² (Coefficient de détermination) : {r2:.4f}")

# Interprétation rapide pour l'utilisateur
print("-" * 30)
if r2 > 0.8:
    print("Performance : EXCELLENTE")
elif r2 > 0.6:
    print("Performance : BONNE")
else:
    print("Performance : À AMÉLIORER (Vérifiez vos données ou hyperparamètres)")

# Sauvegarde du modèle entraîné
joblib.dump(pipeline, "modele_fatigue.pkl")
print("\nModèle sauvegardé sous 'modele_fatigue.pkl'")