// ==========================================
// GRAPHIQUE DU PROFIL JOUEUR
// ==========================================

const barres = document.querySelectorAll(".barre");
const axeY = document.querySelectorAll("#axe-y span");

if (barres.length > 0) {

    let maximum = 0;


    // --------------------------------------
    // Trouver le nombre maximum de points
    // --------------------------------------

    barres.forEach(function (barre) {

        const points = Number(barre.dataset.points);

        if (points > maximum) {
            maximum = points;
        }

    });


    // --------------------------------------
    // Éviter un maximum de 0
    // --------------------------------------

    if (maximum === 0) {
        maximum = 100;
    }


    // --------------------------------------
    // Mettre à jour l'axe Y
    // --------------------------------------

    axeY.forEach(function (element, index) {

        const pourcentage = 1 - (index / 4);

        const valeur = Math.round(
            maximum * pourcentage
        );

        element.textContent = valeur;

    });


    // --------------------------------------
    // Créer les barres
    // --------------------------------------

    barres.forEach(function (barre) {

        const points = Number(
            barre.dataset.points
        );


        let hauteur =
            (points / maximum) * 100;


        // Sécurité
        if (hauteur < 2) {
            hauteur = 2;
        }


        barre.style.height =
            hauteur + "%";


        // Positionner le nombre au-dessus
        const valeur =
            barre.parentElement.querySelector(
                ".valeur-barre"
            );


        if (valeur) {

            valeur.style.bottom =
                "calc(" +
                hauteur +
                "% + 5px)";

        }

    });

}