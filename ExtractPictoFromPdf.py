#!/usr/bin/env python3
"""
Script pour extraire et reconnaître les pictogrammes de danger
dans les Fiches de Données de Sécurité (FDS/MSDS)
"""
from venv import logger

import pdfplumber
from PIL import Image
import io
import base64
import anthropic
import sys
from pathlib import Path
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Dictionnaire des pictogrammes de danger SGH/CLP
PICTOGRAMMES_DANGER = {
    "GHS01": "Explosif",
    "GHS02": "Inflammable",
    "GHS03": "Comburant",
    "GHS04": "Gaz sous pression",
    "GHS05": "Corrosif",
    "GHS06": "Toxique",
    "GHS07": "Nocif/Irritant",
    "GHS08": "Danger pour la santé",
    "GHS09": "Danger pour l'environnement"
}


def extraire_images_pdf(pathPDF, page_debut=0, page_fin=2):
    """
    Extraire les images d'un PDF (généralement les pictogrammes sont sur les premières pages)

    Args:
        pathPDF: Chemin vers la FDS
        page_debut: Première page à analyser (0 = première page)
        page_fin: Dernière page à analyser

    Returns:
        Liste d'images extraites
    """
    images_extraites = []

    print(f"📄 Extraction des images de {pathPDF}...")

    with pdfplumber.open(pathPDF) as pdf:
        nb_pages = min(len(pdf.pages), page_fin + 1)

        for num_page in range(page_debut, nb_pages):
            page = pdf.pages[num_page]
            print(f"  Page {num_page + 1}/{nb_pages}...")

            # Extraire les images de la page
            images = page.images

            for i, img_info in enumerate(images):
                try:
                    # Extraire la zone de l'image
                    bbox = (img_info["x0"], img_info["top"], img_info["x1"], img_info["bottom"])

                    # Convertir en image PIL
                    img = page.within_bbox(bbox).to_image(resolution=200)
                    pil_image = img.original

                    # Filtrer les images trop petites ou trop grandes
                    largeur, hauteur = pil_image.size

                    # Les pictogrammes font généralement 50-200 pixels
                    if 30 < largeur < 400 and 30 < hauteur < 400:
                        images_extraites.append({
                            'image': pil_image,
                            'page': num_page + 1,
                            'numero': i + 1,
                            'bbox': bbox,
                            'taille': (largeur, hauteur)
                        })
                        print(f"    ✓ Image {i + 1} extraite ({largeur}x{hauteur}px)")

                except Exception as e:
                    print(f"    ⚠️  Erreur image {i + 1}: {e}")

    print(f"\n✅ {len(images_extraites)} image(s) extraite(s)\n")
    return images_extraites


def identifier_pictogramme_claude(image_pil):
    """
    Utiliser Claude pour identifier un pictogramme de danger

    Args:
        image_pil: Image PIL du pictogramme

    Returns:
        dict: Informations sur le pictogramme identifié
    """
    try:
        # Convertir l'image PIL en base64
        buffer = io.BytesIO()
        image_pil.save(buffer, format='PNG')
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Créer le client Claude
        client = anthropic.Anthropic()

        # Prompt spécialisé pour les pictogrammes de danger
        prompt = """Analyse cette image et détermine s'il s'agit d'un pictogramme de danger SGH/CLP/GHS.

Si c'est un pictogramme de danger, identifie:
1. Le code (GHS01 à GHS09)
2. Le nom du danger
3. La description

Liste des pictogrammes SGH:
- GHS01: Explosif (bombe qui explose)
- GHS02: Inflammable (flamme)
- GHS03: Comburant (flamme sur cercle)
- GHS04: Gaz sous pression (bouteille de gaz)
- GHS05: Corrosif (tube versant liquide sur main et métal)
- GHS06: Toxique (tête de mort)
- GHS07: Nocif/Irritant (point d'exclamation)
- GHS08: Danger pour la santé (silhouette avec étoile)
- GHS09: Danger pour l'environnement (arbre et poisson morts)

Réponds UNIQUEMENT au format JSON:
{
  "est_pictogramme": true/false,
  "code": "GHS0X" ou null,
  "nom": "Nom du danger" ou null,
  "confiance": 0.0-1.0
}"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )

        # Parser la réponse JSON
        import json
        reponse_texte = message.content[0].text

        # Nettoyer la réponse (enlever les markdown si présents)
        reponse_texte = reponse_texte.strip()
        if reponse_texte.startswith('```'):
            reponse_texte = reponse_texte.split('\n', 1)[1]
            reponse_texte = reponse_texte.rsplit('```', 1)[0]

        resultat = json.loads(reponse_texte)
        return resultat

    except Exception as e:
        print(f"❌ Erreur identification Claude: {e}")
        return None


def analyser_fds(pathPDF, sauvegarder_images=False):
    """
    Analyser une FDS complète pour extraire tous les pictogrammes

    Args:
        pathPDF: Chemin vers la FDS
        sauvegarder_images: Si True, sauvegarde les images extraites

    Returns:
        Liste des pictogrammes identifiés
    """
    logging.debug("=" * 70)
    logging.debug("🔬 ANALYSE DE FICHE DE DONNÉES DE SÉCURITÉ (FDS)")
    logging.debug("=" * 70)

    # Extraire les images
    images = extraire_images_pdf(pathPDF, page_debut=0, page_fin=3)

    if not images:
        logging.debug("⚠️  Aucune image trouvée dans le PDF")
        return []

    # Créer un dossier pour les images si demandé
    if sauvegarder_images:
        dossier_images = Path("pictogrammes_extraits")
        dossier_images.mkdir(exist_ok=True)

    # Identifier chaque image
    pictogrammes_identifies = []

    logging.debug("🔍 IDENTIFICATION DES PICTOGRAMMES")
    logging.debug("-" * 70)

    for idx, img_info in enumerate(images, 1):
        logging.debug(f"\n📊 Image {idx}/{len(images)} (Page {img_info['page']})...")

        # Identifier avec Claude
        resultat = identifier_pictogramme_claude(img_info['image'])

        if resultat and resultat.get('est_pictogramme'):
            code = resultat.get('code')
            nom = resultat.get('nom')
            confiance = resultat.get('confiance', 0)

            logging.debug(f"  ✅ PICTOGRAMME IDENTIFIÉ:")
            logging.debug(f"     Code: {code}")
            logging.debug(f"     Danger: {nom}")
            logging.debug(f"     Confiance: {confiance * 100:.0f}%")

            pictogrammes_identifies.append({
                'code': code,
                'nom': nom,
                'confiance': confiance,
                'page': img_info['page'],
                'image': img_info['image']
            })

            # Sauvegarder l'image si demandé
            if sauvegarder_images:
                nom_fichier = f"{code}_{idx}.png"
                chemin_sauvegarde = dossier_images / nom_fichier
                img_info['image'].save(chemin_sauvegarde)
                print(f"     💾 Sauvegardé: {chemin_sauvegarde}")
        else:
            logging.debug(f"  ⚠️  Pas un pictogramme de danger")

    return pictogrammes_identifies


def generer_rapport(pictogrammes, pathPDF):
    """
    Générer un rapport des pictogrammes identifiés
    """
    print("\n" + "=" * 70)
    print("📋 RAPPORT D'ANALYSE")
    print("=" * 70)
    print(f"\nFichier analysé: {pathPDF}")
    print(f"Nombre de pictogrammes identifiés: {len(pictogrammes)}")

    if pictogrammes:
        print("\n🚨 DANGERS IDENTIFIÉS:")
        print("-" * 70)

        for picto in pictogrammes:
            print(f"\n  • {picto['code']}: {picto['nom']}")
            print(f"    Confiance: {picto['confiance'] * 100:.0f}%")
            print(f"    Page: {picto['page']}")

        # Sauvegarder le rapport
        nom_rapport = Path(pathPDF).stem + "_rapport_pictogrammes.txt"
        with open(nom_rapport, 'w', encoding='utf-8') as f:
            f.write(f"RAPPORT D'ANALYSE - PICTOGRAMMES DE DANGER\n")
            f.write(f"=" * 70 + "\n\n")
            f.write(f"Fichier: {pathPDF}\n")
            f.write(f"Nombre de pictogrammes: {len(pictogrammes)}\n\n")
            f.write(f"DANGERS IDENTIFIÉS:\n")
            f.write("-" * 70 + "\n\n")

            for picto in pictogrammes:
                f.write(f"{picto['code']}: {picto['nom']}\n")
                f.write(f"  Confiance: {picto['confiance'] * 100:.0f}%\n")
                f.write(f"  Page: {picto['page']}\n\n")

        print(f"\n💾 Rapport sauvegardé: {nom_rapport}")
    else:
        print("\n⚠️  Aucun pictogramme de danger identifié")

    print("\n" + "=" * 70)


def main():
    """Fonction principale"""

    if len(sys.argv) < 2:
        print("Usage: python fds_pictogrammes.py <fichier_fds.pdf> [--save-images]")
        print("\nExemple:")
        print("  python fds_pictogrammes.py ma_fiche_securite.pdf")
        print("  python fds_pictogrammes.py ma_fiche_securite.pdf --save-images")
        sys.exit(1)

    pathPDF = sys.argv[1]
    sauvegarder_images = '--save-images' in sys.argv

    # Vérifier que le fichier existe
    if not Path(pathPDF).exists():
        print(f"❌ Fichier non trouvé: {pathPDF}")
        sys.exit(1)

    # Analyser la FDS
    pictogrammes = analyser_fds(pathPDF, sauvegarder_images)

    # Générer le rapport
    generer_rapport(pictogrammes, pathPDF)

    print("\n✨ Analyse terminée!\n")


if __name__ == "__main__":
    main()