from flask import Flask, render_template, request
from calcul import calculer_points

app = Flask(__name__)


@app.route("/")
def accueil():
    return render_template("index.html")


@app.route("/simulation", methods=["GET", "POST"])
def simulation():

    if request.method == "POST":

        niveau = request.form.get("niveau")
        nombre_paires = request.form.get("nombre_paires")
        place = request.form.get("place")
        sexe = request.form.get("sexe")

        try:
            nombre_paires = int(nombre_paires)
            place = int(place)
        except (TypeError, ValueError):
            return render_template(
                "index.html",
                erreur="Veuillez entrer des nombres valides."
            )

        # Vérifications
        if nombre_paires < 4:
            return render_template(
                "index.html",
                erreur="Un tournoi doit comporter au moins 4 paires."
            )

        if place < 1 or place > nombre_paires:
            return render_template(
                "index.html",
                erreur="La place doit être comprise entre 1 et le nombre de paires."
            )

        # P500 et P1000 nécessitent le sexe
        if niveau in ["P500", "P1000"] and sexe not in ["messieurs", "dames"]:
            return render_template(
                "index.html",
                erreur="Veuillez sélectionner Messieurs ou Dames."
            )

        points = calculer_points(
            niveau,
            nombre_paires,
            place,
            sexe
        )

        if points is None:
            return render_template(
                "index.html",
                erreur="Impossible de calculer les points avec ces informations."
            )

        return render_template(
            "resultat.html",
            niveau=niveau,
            nombre_paires=nombre_paires,
            place=place,
            sexe=sexe,
            points=points
        )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)