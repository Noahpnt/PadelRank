from flask import Flask, render_template, request, session, redirect, url_for

from calcul import calculer_points

from database import (
    initialiser_base,
    initialiser_table_simulations,
    recuperer_joueurs,
    recuperer_joueur,
    rechercher_joueur,
    ajouter_simulation,
    recuperer_simulations,
    mettre_a_jour_points_joueur,
    mettre_a_jour_classements,
    recuperer_evolution_points,
    recuperer_statistiques_joueur,
    creer_utilisateur,
    rechercher_utilisateur,
    verifier_mot_de_passe,
    recuperer_utilisateur,
)

from datetime import datetime


# ==========================================
# CONFIGURATION
# ==========================================

app = Flask(__name__)
app.secret_key = "padelrank-cle-secrete-2026"


# ==========================================
# INITIALISATION DE LA BASE DE DONNÉES
# ==========================================

initialiser_base()
initialiser_table_simulations()
mettre_a_jour_classements()


# ==========================================
# PAGE D'ACCUEIL
# ==========================================

@app.route("/")
def accueil():

    return render_template("index.html")


@app.route("/inscription", methods=["GET", "POST"])
def inscription():

    if request.method == "POST":

        prenom = request.form.get(
            "prenom",
            ""
        ).strip()

        nom = request.form.get(
            "nom",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        mot_de_passe = request.form.get(
            "mot_de_passe",
            ""
        )

        confirmation = request.form.get(
            "confirmation",
            ""
        )


        if not prenom or not nom or not email or not mot_de_passe:

            return render_template(
                "inscription.html",
                erreur="Tous les champs sont obligatoires.",
                prenom=prenom,
                nom=nom,
                email=email
            )


        if mot_de_passe != confirmation:

            return render_template(
                "inscription.html",
                erreur="Les deux mots de passe ne correspondent pas.",
                prenom=prenom,
                nom=nom,
                email=email
            )


        if len(mot_de_passe) < 6:

            return render_template(
                "inscription.html",
                erreur="Le mot de passe doit contenir au moins 6 caractères.",
                prenom=prenom,
                nom=nom,
                email=email
            )


        utilisateur_existant = rechercher_utilisateur(
            email
        )


        if utilisateur_existant is not None:

            return render_template(
                "inscription.html",
                erreur="Cette adresse email est déjà utilisée.",
                prenom=prenom,
                nom=nom,
                email=email
            )


        utilisateur_id = creer_utilisateur(
            nom,
            prenom,
            email,
            mot_de_passe
        )


        if utilisateur_id is None:

            return render_template(
                "inscription.html",
                erreur="Impossible de créer le compte.",
                prenom=prenom,
                nom=nom,
                email=email
            )


        return render_template(
            "connexion.html",
            succes="Compte créé avec succès ! Tu peux maintenant te connecter."
        )


    return render_template(
        "inscription.html"
    )



@app.route("/connexion", methods=["GET", "POST"])
def connexion():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        mot_de_passe = request.form.get(
            "mot_de_passe",
            ""
        )


        utilisateur = rechercher_utilisateur(
            email
        )


        if utilisateur is None:

            return render_template(
                "connexion.html",
                erreur="Email ou mot de passe incorrect.",
                email=email
            )


        if not verifier_mot_de_passe(
            mot_de_passe,
            utilisateur["mot_de_passe"]
        ):

            return render_template(
                "connexion.html",
                erreur="Email ou mot de passe incorrect.",
                email=email
            )


        session["utilisateur_id"] = utilisateur["id"]

        session["utilisateur_nom"] = (
            utilisateur["prenom"]
        )


        return redirect(
            url_for("accueil")
        )


    return render_template(
        "connexion.html"
    )


@app.route("/deconnexion")
def deconnexion():

    session.clear()

    return redirect(
        url_for("accueil")
    )

@app.route("/mon-compte")
def mon_compte():

    if "utilisateur_id" not in session:

        return redirect(
            url_for("connexion")
        )


    utilisateur = recuperer_utilisateur(
        session["utilisateur_id"]
    )


    if utilisateur is None:

        session.clear()

        return redirect(
            url_for("connexion")
        )


    return render_template(
        "mon_compte.html",
        utilisateur=utilisateur
    )


# ==========================================
# PAGE SIMULATION
# ==========================================

@app.route("/simulation", methods=["GET", "POST"])
def simulation():

    if request.method == "POST":

        # --------------------------------------
        # RÉCUPÉRATION DU JOUEUR
        # --------------------------------------

        prenom = request.form.get("prenom", "").strip()
        nom = request.form.get("nom", "").strip()

        if not prenom or not nom:

            return render_template(
                "simulation.html",
                erreur="Veuillez renseigner votre prénom et votre nom.",
                prenom=prenom,
                nom=nom
            )

        joueur = rechercher_joueur(nom, prenom)

        if joueur is None:

            return render_template(
                "simulation.html",
                erreur="Joueur introuvable. Vérifie le prénom et le nom.",
                prenom=prenom,
                nom=nom
            )


        # --------------------------------------
        # RÉCUPÉRATION DES INFORMATIONS
        # --------------------------------------

        points = joueur["points"]

        niveau = request.form.get("niveau", "").strip()

        try:
            paires = int(request.form.get("paires", 0))
            place = int(request.form.get("place", 0))
        except ValueError:

            return render_template(
                "simulation.html",
                erreur="Le nombre de paires et la place doivent être des nombres.",
                prenom=prenom,
                nom=nom
            )

        sexe = request.form.get("sexe")


        # --------------------------------------
        # CALCUL DES POINTS
        # --------------------------------------

        points_gagnes = calculer_points(
            niveau,
            paires,
            place,
            sexe
        )

        if points_gagnes is None:

            return render_template(
                "simulation.html",
                erreur="Impossible de calculer les points avec ces informations.",
                prenom=prenom,
                nom=nom
            )


        # --------------------------------------
        # CALCUL DU NOUVEAU TOTAL
        # --------------------------------------

        nouveau_total = points + points_gagnes


        # --------------------------------------
        # DATE DE LA SIMULATION
        # --------------------------------------

        date_simulation = datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        )


        # --------------------------------------
        # MISE À JOUR DU JOUEUR
        # --------------------------------------

        mettre_a_jour_points_joueur(
            joueur_id=joueur["id"],
            nouveau_total=nouveau_total,
            date=date_simulation
        )


        # --------------------------------------
        # ENREGISTREMENT DE LA SIMULATION
        # --------------------------------------

        ajouter_simulation(
            joueur_id=joueur["id"],
            niveau=niveau,
            nombre_paires=paires,
            place=place,
            points_gagnes=points_gagnes,
            ancien_total=points,
            nouveau_total=nouveau_total,
            date_simulation=date_simulation
        )


        # --------------------------------------
        # MISE À JOUR DU CLASSEMENT
        # --------------------------------------

        mettre_a_jour_classements()


        # --------------------------------------
        # AFFICHAGE DU RÉSULTAT
        # --------------------------------------

        return render_template(
            "resultat.html",
            points=points,
            nouveau_total=nouveau_total,
            points_gagnes=points_gagnes,
            niveau=niveau,
            paires=paires,
            place=place,
            sexe=sexe,
            joueur=joueur
        )


    # --------------------------------------
    # AFFICHAGE INITIAL DU FORMULAIRE
    # --------------------------------------

    return render_template("simulation.html")


# ==========================================
# PAGE CLASSEMENT
# ==========================================

@app.route("/classement")
def classement():

    recherche = request.args.get(
        "recherche",
        ""
    ).strip()

    joueurs = recuperer_joueurs(recherche)

    return render_template(
        "classement.html",
        joueurs=joueurs,
        recherche=recherche
    )


# ==========================================
# PAGE PROFIL JOUEUR
# ==========================================

@app.route("/joueur/<int:id_joueur>")
def profil_joueur(id_joueur):

    joueur = recuperer_joueur(id_joueur)

    if joueur is None:
        return "Joueur introuvable", 404

    simulations = recuperer_simulations(id_joueur)

    evolution = recuperer_evolution_points(id_joueur)

    statistiques = recuperer_statistiques_joueur(id_joueur)

    return render_template(
        "joueur.html",
        joueur=joueur,
        simulations=simulations,
        evolution=evolution,
        statistiques=statistiques
    )


# ==========================================
# LANCEMENT
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)