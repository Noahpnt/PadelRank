import sqlite3

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


DATABASE = "padelrank.db"


# ==========================================
# CONNEXION À LA BASE
# ==========================================

def get_connection():

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    return connection


# ==========================================
# INITIALISATION DE LA BASE
# ==========================================

def initialiser_base():

    connection = get_connection()
    cursor = connection.cursor()


    # ======================================
    # TABLE DES JOUEURS
    # ======================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS joueurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            points INTEGER DEFAULT 0,
            classement INTEGER,
            derniere_mise_a_jour TEXT
        )
    """)


    # ======================================
    # TABLE DES UTILISATEURS
    # ======================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            mot_de_passe TEXT NOT NULL,
            date_creation TEXT NOT NULL,
            joueur_id INTEGER,
            FOREIGN KEY (joueur_id)
                REFERENCES joueurs(id)
        )
    """)


    # ======================================
    # AJOUT DE joueur_id SI NÉCESSAIRE
    # ======================================

    cursor.execute("""
        PRAGMA table_info(utilisateurs)
    """)

    colonnes_utilisateurs = [
        colonne["name"]
        for colonne in cursor.fetchall()
    ]


    if "joueur_id" not in colonnes_utilisateurs:

        cursor.execute("""
            ALTER TABLE utilisateurs
            ADD COLUMN joueur_id INTEGER
        """)


    # ======================================
    # TABLE DES SIMULATIONS
    # ======================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            joueur_id INTEGER NOT NULL,
            niveau TEXT NOT NULL,
            nombre_paires INTEGER NOT NULL,
            place INTEGER NOT NULL,
            points_gagnes INTEGER NOT NULL,
            ancien_total INTEGER NOT NULL,
            nouveau_total INTEGER NOT NULL,
            date_simulation TEXT NOT NULL,
            FOREIGN KEY (joueur_id)
                REFERENCES joueurs(id)
        )
    """)


    connection.commit()
    connection.close()


    # Vérification d'une éventuelle ancienne
    # version de la table simulations
    migrer_ancienne_table_simulations()


# ==========================================
# MIGRATION ANCIENNE TABLE SIMULATIONS
# ==========================================

def migrer_ancienne_table_simulations():

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute("""
        PRAGMA table_info(simulations)
    """)

    colonnes = [
        colonne["name"]
        for colonne in cursor.fetchall()
    ]


    # La table est déjà correcte
    if (
        "nombre_paires" in colonnes
        and "ancien_total" in colonnes
        and "nouveau_total" in colonnes
        and "date_simulation" in colonnes
    ):

        connection.close()

        return


    # Ancienne table détectée
    cursor.execute("""
        ALTER TABLE simulations
        RENAME TO simulations_ancienne
    """)


    cursor.execute("""
        CREATE TABLE simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            joueur_id INTEGER NOT NULL,
            niveau TEXT NOT NULL,
            nombre_paires INTEGER NOT NULL,
            place INTEGER NOT NULL,
            points_gagnes INTEGER NOT NULL,
            ancien_total INTEGER NOT NULL,
            nouveau_total INTEGER NOT NULL,
            date_simulation TEXT NOT NULL,
            FOREIGN KEY (joueur_id)
                REFERENCES joueurs(id)
        )
    """)


    cursor.execute("""
        SELECT *
        FROM simulations_ancienne
    """)

    anciennes = cursor.fetchall()


    for simulation in anciennes:

        ancien_total = (
            simulation["total_apres"]
            - simulation["points_gagnes"]
        )


        cursor.execute("""
            INSERT INTO simulations (
                joueur_id,
                niveau,
                nombre_paires,
                place,
                points_gagnes,
                ancien_total,
                nouveau_total,
                date_simulation
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            simulation["joueur_id"],
            simulation["niveau"],
            simulation["paires"],
            simulation["place"],
            simulation["points_gagnes"],
            ancien_total,
            simulation["total_apres"],
            simulation["date"] or "Date inconnue"
        ))


    cursor.execute("""
        DROP TABLE simulations_ancienne
    """)


    connection.commit()
    connection.close()


# ==========================================
# AJOUTER UN JOUEUR
# ==========================================

def ajouter_joueur(
    nom,
    prenom,
    points,
    classement
):

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute("""
        INSERT INTO joueurs (
            nom,
            prenom,
            points,
            classement
        )
        VALUES (?, ?, ?, ?)
    """, (
        nom,
        prenom,
        points,
        classement
    ))


    connection.commit()
    connection.close()


# ==========================================
# JOUEURS DE TEST
# ==========================================

def ajouter_joueurs_test():

    joueurs_test = [
        ("Martin", "Lucas", 1580),
        ("Bernard", "Hugo", 1420),
        ("Robert", "Nathan", 980),
        ("Moreau", "Jules", 1760)
    ]


    connection = get_connection()
    cursor = connection.cursor()


    for nom, prenom, points in joueurs_test:

        cursor.execute("""
            SELECT id
            FROM joueurs
            WHERE LOWER(nom) = LOWER(?)
            AND LOWER(prenom) = LOWER(?)
        """, (
            nom,
            prenom
        ))


        joueur = cursor.fetchone()


        if joueur is None:

            cursor.execute("""
                INSERT INTO joueurs (
                    nom,
                    prenom,
                    points
                )
                VALUES (?, ?, ?)
            """, (
                nom,
                prenom,
                points
            ))


    connection.commit()
    connection.close()


# ==========================================
# METTRE À JOUR LES POINTS
# ==========================================

def mettre_a_jour_points_joueur(
    joueur_id,
    nouveau_total,
    date
):

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute("""
        UPDATE joueurs
        SET points = ?,
            derniere_mise_a_jour = ?
        WHERE id = ?
    """, (
        nouveau_total,
        date,
        joueur_id
    ))


    connection.commit()
    connection.close()


# ==========================================
# METTRE À JOUR LES CLASSEMENTS
# ==========================================

def mettre_a_jour_classements():

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute("""
        SELECT id
        FROM joueurs
        ORDER BY points DESC
    """)


    joueurs = cursor.fetchall()


    for rang, joueur in enumerate(
        joueurs,
        start=1
    ):

        cursor.execute("""
            UPDATE joueurs
            SET classement = ?
            WHERE id = ?
        """, (
            rang,
            joueur["id"]
        ))


    connection.commit()
    connection.close()


# ==========================================
# RÉCUPÉRER LES JOUEURS
# ==========================================

def recuperer_joueurs(recherche=""):

    connection = get_connection()
    cursor = connection.cursor()


    if recherche:

        recherche = f"%{recherche.lower()}%"


        cursor.execute("""
            SELECT *
            FROM joueurs
            WHERE LOWER(nom) LIKE ?
               OR LOWER(prenom) LIKE ?
               OR LOWER(prenom || ' ' || nom) LIKE ?
               OR LOWER(nom || ' ' || prenom) LIKE ?
            ORDER BY points DESC
        """, (
            recherche,
            recherche,
            recherche,
            recherche
        ))


    else:

        cursor.execute("""
            SELECT *
            FROM joueurs
            ORDER BY points DESC
        """)


    joueurs = cursor.fetchall()

    connection.close()

    return joueurs


# ==========================================
# RÉCUPÉRER UN JOUEUR
# ==========================================

def recuperer_joueur(id_joueur):

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute("""
        SELECT *
        FROM joueurs
        WHERE id = ?
    """, (
        id_joueur,
    ))


    joueur = cursor.fetchone()

    connection.close()

    return joueur


# ==========================================
# RECHERCHER UN JOUEUR
# ==========================================

def rechercher_joueur(
    nom,
    prenom
):

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute("""
        SELECT *
        FROM joueurs
        WHERE LOWER(nom) = LOWER(?)
        AND LOWER(prenom) = LOWER(?)
    """, (
        nom,
        prenom
    ))


    joueur = cursor.fetchone()

    connection.close()

    return joueur


# ==========================================
# AJOUTER UNE SIMULATION
# ==========================================

def ajouter_simulation(
    joueur_id,
    niveau,
    nombre_paires,
    place,
    points_gagnes,
    ancien_total,
    nouveau_total,
    date_simulation
):

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute("""
        INSERT INTO simulations (
            joueur_id,
            niveau,
            nombre_paires,
            place,
            points_gagnes,
            ancien_total,
            nouveau_total,
            date_simulation
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        joueur_id,
        niveau,
        nombre_paires,
        place,
        points_gagnes,
        ancien_total,
        nouveau_total,
        date_simulation
    ))


    connection.commit()
    connection.close()


# ==========================================
# RÉCUPÉRER LES SIMULATIONS
# ==========================================

def recuperer_simulations(joueur_id):

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute("""
        SELECT *
        FROM simulations
        WHERE joueur_id = ?
        ORDER BY id DESC
    """, (
        joueur_id,
    ))


    simulations = cursor.fetchall()

    connection.close()

    return simulations


# ==========================================
# ÉVOLUTION DES POINTS
# ==========================================

def recuperer_evolution_points(joueur_id):

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            date_simulation,
            ancien_total,
            nouveau_total,
            points_gagnes
        FROM simulations
        WHERE joueur_id = ?
        ORDER BY id ASC
    """, (
        joueur_id,
    ))


    evolution = cursor.fetchall()

    connection.close()

    return evolution


# ==========================================
# STATISTIQUES
# ==========================================

def recuperer_statistiques_joueur(
    joueur_id
):

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            COUNT(*) AS nombre_simulations,
            COALESCE(
                SUM(points_gagnes),
                0
            ) AS total_points_gagnes,
            COALESCE(
                MAX(points_gagnes),
                0
            ) AS meilleur_gain
        FROM simulations
        WHERE joueur_id = ?
    """, (
        joueur_id,
    ))


    statistiques = cursor.fetchone()

    connection.close()

    return statistiques


# ==========================================
# CRÉER UN UTILISATEUR + SON JOUEUR
# ==========================================

def creer_utilisateur(
    nom,
    prenom,
    email,
    mot_de_passe
):

    connection = get_connection()
    cursor = connection.cursor()


    mot_de_passe_hash = generate_password_hash(
        mot_de_passe
    )


    try:

        # -------------------------------
        # CRÉATION DU JOUEUR
        # -------------------------------

        cursor.execute("""
            INSERT INTO joueurs (
                nom,
                prenom,
                points,
                classement
            )
            VALUES (?, ?, ?, ?)
        """, (
            nom,
            prenom,
            0,
            None
        ))


        joueur_id = cursor.lastrowid


        # -------------------------------
        # CRÉATION DU COMPTE
        # -------------------------------

        cursor.execute("""
            INSERT INTO utilisateurs (
                nom,
                prenom,
                email,
                mot_de_passe,
                date_creation,
                joueur_id
            )
            VALUES (?, ?, ?, ?, datetime('now'), ?)
        """, (
            nom,
            prenom,
            email,
            mot_de_passe_hash,
            joueur_id
        ))


        utilisateur_id = cursor.lastrowid


        connection.commit()

        connection.close()


        # Recalcul du classement
        mettre_a_jour_classements()


        return utilisateur_id


    except sqlite3.IntegrityError:

        connection.rollback()
        connection.close()

        return None


# ==========================================
# RECHERCHER UN UTILISATEUR
# ==========================================

def rechercher_utilisateur(email):

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute("""
        SELECT *
        FROM utilisateurs
        WHERE LOWER(email) = LOWER(?)
    """, (
        email,
    ))


    utilisateur = cursor.fetchone()

    connection.close()

    return utilisateur


# ==========================================
# RÉCUPÉRER UN UTILISATEUR
# ==========================================

def recuperer_utilisateur(
    utilisateur_id
):

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute("""
        SELECT *
        FROM utilisateurs
        WHERE id = ?
    """, (
        utilisateur_id,
    ))


    utilisateur = cursor.fetchone()

    connection.close()

    return utilisateur


# ==========================================
# VÉRIFIER LE MOT DE PASSE
# ==========================================

def verifier_mot_de_passe(
    mot_de_passe,
    mot_de_passe_hash
):

    return check_password_hash(
        mot_de_passe_hash,
        mot_de_passe
    )


# ==========================================
# COMPATIBILITÉ AVEC APP.PY
# ==========================================

def initialiser_table_simulations():

    initialiser_base()


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    initialiser_base()

    ajouter_joueurs_test()

    mettre_a_jour_classements()

    print(
        "Base de données initialisée "
        "et joueurs de test ajoutés !"
    )