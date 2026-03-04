# -*- coding: utf-8 -*-
import re
import string

defaultFile="/Users/jeanpaulcognet/Documents/Praggma/Projets/Soledi/Etiquettes/ExempleEtiquettes/ACETONE 1l.lbl"
defaultStart=0
defaultLength=999999999
def afficher_caracteres(fileName,min,max):
    print(f"afficher_caracteres({fileName},{min},{max})")
    imprimable_re = re.compile(r'[A-Za-z0-9, :-_()\'éèà/]+')
    imprimable_hex = re.compile(r'0x([2-7]|E|0A|C[98]|F[9ABC])')
    marque_text = re.compile(r'Texte[0-9]+')
    marque_codebarre = re.compile(r'3(\d{12})+')
    marque_image = re.compile(r'jpg')

    try:
        with open(fileName, "r", encoding="iso-8859-1", errors="replace") as f:
            contenu = f.read()
        current_printable = ""
        baliseTexte=""
        for i, c in enumerate(contenu):
            code_hex = f"0x{ord(c):02X}"
#            if code_hex =='0x00':
#                continue
            if (code_hex == '0x92') or (code_hex == '0x19'):
                c="'"
                code_hex = "0x27"
            if imprimable_hex.match(code_hex):
                affichage = c
                current_printable = current_printable + c
            else:
                affichage = '-'
            # Représentation lisible (affiche . pour les caractères non imprimables)
                if current_printable != "":
                    if (i >= min) and (i < min + max):
                        if len(current_printable) >= 5:
                            if (marque_codebarre.match(current_printable)):
                                print(f"CodeBarre\t{current_printable}")
                            if (marque_image.search(current_printable)):
                                print(f"Image\t{current_printable}")
                            if (marque_text.match(current_printable)):
                                baliseTexte=current_printable
                            else:
                                if baliseTexte != "":
#                                    print(f"Position {i:04d} : {baliseTexte} {current_printable} ->'{affichage}' -> {code_hex}")
                                    print(f"{baliseTexte}\t{current_printable}")
                                    baliseTexte=''
                current_printable = ""

    except FileNotFoundError:
        print(f"Erreur : le fichier '{fileName}' est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

def ask_value_default(prompt,defaultValue):
    askedValue = input(f"{prompt} : {defaultValue} : ")
    if (askedValue == ""):
        return defaultValue
    else:
        return askedValue




# Exemple d'utilisation
if __name__ == "__main__":
    fileName = ask_value_default("Entrez le chemin du fichier à lire",defaultFile)
    start=int(ask_value_default("Début de scan",defaultStart))
    scanLength=int(ask_value_default("Longueur du scan",defaultLength))
    afficher_caracteres(fileName,start,scanLength)

