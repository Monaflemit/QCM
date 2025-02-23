# cd C:\Users\quewa\Documents\pyzo\QCM
# streamlit run QCM.py
import streamlit as st
from streamlit import write
from IPython.display import display, Latex
import io
import sys
import re
import textwrap 
    

from time import sleep,time


from PIL import Image, ImageDraw, ImageFont
import nbformat as nbf



#afficher les images de qcm.py
#Pouvoir sélectionner un qcm


# Attendre 1 seconde
#sleep(1)



# Charger le contenu du fichier
with open("QCM.ipynb", "r", encoding='utf-8') as f:
    notebook_content = nbf.read(f, as_version=4)
#premiere_cellule = notebook_content.cells[0]

try:
    zone=st.session_state.zone # 1 2 3
    i=st.session_state.i# Numéro de la Q
    classe=st.session_state.classe
    correct=st.session_state.correct #[1,1,2]
    responses=st.session_state.responses#[0,0,0]
    if st.session_state.zone>3:
        if responses==correct: #monter d'une classe
            classe=["6","5","4","3","2","1","T","L1","L2","L3","M1","M2"][["6","5","4","3","2","1","T","L1","L2","L3","M1","M2"].index(classe)+1]
        zone=1
        i+=1
        while not("q"+classe in notebook_content.cells[i].source or "q"+classe.lower() in notebook_content.cells[i].source):
            i+=1        # mettre à la place i avec q5
            if i >= len(notebook_content.cells):
                i=0
        print(i)    
        responses=[0,0,0]
    st.session_state.restart=0
    user_code=st.session_state.user_code 

    #st.write(zone)
except:
    st.write("Restart")
    classe="6"
    correct=[0,0,0] #0 Neutre 1 vrai 2 faux
    zone=1  #Q1 2 3
    i=0#cellule i
    responses=[0,0,0]#0 pas répondu 1 rep1 2 rep2
    st.session_state.i=i
    st.session_state.zone=zone
    st.session_state.correct=correct
    st.session_state.classe=classe   
    st.session_state.responses=responses
    try:
        a=st.session_state.restart
    except:
        st.session_state.restart=0
    st.session_state.last_click = None  # Aucun clic initialement
    st.session_state.user_code = ""
    st.session_state.triche=0 #st.session_state.triche=1

# Titre
st.title(classe)

#st.write(zone)



# Fonction pour ajouter du texte sur une image
def add_text_to_image(image_path, text, position, font_size=20, color=(0, 0, 0)):#color=(255, 255, 255)
    # Ouvrir l'image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # Utiliser une police intégrée
    font = ImageFont.load_default()
    
    # Si vous avez une police TTF, vous pouvez la charger comme suit :
    # font = ImageFont.truetype("path/to/font.ttf", font_size
    
    # Ajouter le texte sur l'image
    draw.text(position, text, fill=color, font=font)
    
    return image

def execute_code_segment(cell_source,segment): #Pour éxécuter de q6 à rep2   #segment 1 2 3 
    # Découper le code en lignes
    lines = cell_source.split('\n')
    
    # Trouver les indices des premières occurrences de "q6" et "rep2"
    start_index = None
    end_index = None
    seg=1
    for i, line in enumerate(lines):
        #st.write(start_index,seg,segment,end_index)
        if start_index is None and line.startswith("q"):
            if seg==segment:
                start_index = i
                #print(seg,segment)
            else:
                seg+=1
        elif start_index is not None and "rep2" in line:
            end_index = i
            break
    
    # Si on a trouvé les deux indices, extraire et exécuter le segment de code
    if start_index is not None and end_index is not None:
        code_segment = "\n".join(lines[start_index:end_index + 1])
        
        #st.write(segment)
        #st.write("Code à exécuter :\n", code_segment)
        
        # Déterminer la valeur de brep en fonction de la présence de #
        for line in lines[start_index:end_index + 1]:
            if "rep1" in line and "#" in line:
                brep = 1 #bonne réponse
            elif "rep2" in line and "#" in line:
                brep = 2
        
        # Ajouter brep au segment de code
        code_segment += f"\nbrep = {brep}"
        
        # Exécuter le segment de code en utilisant exec (attention aux risques de sécurité)
        local_vars = {}
        exec(code_segment, {}, local_vars)  # pour images à insérer à mettre en dehors du def
        return local_vars
    else:
        #print("Segment de code non trouvé.")
        return None

# Fonction pour ajouter une image sur une image principale avec transparence
def add_image_to_image(background_path, overlay_path, position):
    background = Image.open(background_path).convert("RGBA")
    
    
    # Créer une nouvelle image avec la même taille que l'arrière-plan
    new_image = Image.new("RGBA", background.size)
    
    # Coller l'image de fond
    new_image.paste(background, (0, 0))
    
    for i in range(len(overlay_path)) :
        overlay = Image.open(overlay_path[i]).convert("RGBA")
        
         # Redimensionner l'image superposée à la moitié de sa taille
        overlay = overlay.resize((overlay.width // 2, overlay.height // 2), Image.ANTIALIAS)
             
        
        # Coller l'image superposée avec le masque de transparence
        new_image.paste(overlay, position[i], overlay)
    
    return new_image

# Images sur la même ligne
col1, col2, col3 = st.columns([1, 2, 1])

# Image 1
with col1:
    # Chemin de votre image
    image_path = "image/t1.png"
    
    # Texte de base à ajouter
    text = "Indications : \n"
    
    # Position du texte sur l'image (x, y)
    position = (15, 15)  # Ajustez selon vos besoins
    
    # Vérifier s'il y a des réponses fausses dans la liste `correct`
    if any(responses[i] != correct[i] and responses[i] != 0 for i in range(3)):  # Si au moins une réponse est incorrecte
        # Ajouter les indices pour chaque réponse fausse
        indices = "Réfléchissez."
        
        
        try:
            # Utilisation d'une expression régulière pour extraire le contenu de ind
            match = re.search(r'ind="(.*?)"\s*$', notebook_content.cells[i].source, re.DOTALL)
            print(match)
            indices = match.group(1)
            # Remplacement de "/n" par "\n"
            indices = indices.replace("/n", "\n")
            # Ajout de retours à la ligne tous les 20 caractères
            indices = textwrap.fill(indices, width=20)
            #print(notebook_content.cells[i].source)
        except Exception as e:
            indices = "échec"
            print(f"Erreur dans le try de indices : {e}")  # Afficher l'erreur
 
        text += indices
    
    # Ajouter le texte sur l'image
    image_with_text = add_text_to_image(image_path, text, position)
    
    # Afficher l'image avec le texte sur Streamlit
    st.image(image_with_text, caption='', use_column_width=True)


    

   
from PIL import Image, ImageDraw, ImageFont
from streamlit_drawable_canvas import st_canvas
from random import randint

with col2:
    image_path = "image/t2.png"
    answer1_text = "Réponse 1"
    answer2_text = "Réponse 2"
    answer1_position = (50, 125)
    answer2_position = (250, 125)

    # Texte à ajouter
    text = "Question : "
    
    # Position du texte sur l'image (x, y)
    position = (15, 15)  # Ajustez selon vos besoins
    
    # Ouvrir l'image
    image = Image.open(image_path).convert("RGBA")
    draw = ImageDraw.Draw(image)
    
    # Utiliser une police intégrée
    font = ImageFont.load_default()
    
    # Si vous avez une police TTF, vous pouvez la charger comme suit :
    #font = ImageFont.truetype("path/to/font.ttf", font_size)
    

    
#     i=randint(1, len(notebook_content.cells))
#  
# 
#     while not("q6" in notebook_content.cells[i].source):
#         i+=randint(1, 5)
#         i=i%len(notebook_content.cells)
    #st.write("result : ",zone)
    #st.write("result : ",st.session_state.zone)
    result=execute_code_segment(notebook_content.cells[i].source,zone)    
    #zone=zone+1
    

    
    # Mettre à jour toutes les variables contenues dans result
    if result:
        for var_name, var_value in result.items():
            globals()[var_name] = var_value


    
    def analyser_sharps(cell_source):
        # liste des bonnes réponses
        # Découper le code en lignes
        lines = cell_source.split('\n')
        
        # Variables pour stocker les positions des commentaires '#'
        rep1_to_rep2_sharps = []
        rep2_to_next_question_sharps = []
        
        # Variables de suivi
        inside_rep1_to_rep2 = False
        inside_rep2_to_q = False
    
        l=[]
        
        # Parcourir chaque ligne
        for i, line in enumerate(lines):
            # Vérifier si la ligne contient 'rep1'
            if 'rep1' in line:
                inside_rep1_to_rep2 = True
                inside_rep2_to_q = False  # Reset pour éviter des erreurs
            # Vérifier si la ligne contient 'rep2'
            elif 'rep2' in line:
                inside_rep1_to_rep2 = False
                inside_rep2_to_q = True
            # Vérifier si la ligne contient 'q' mais pas 'rep1' ou 'rep2' (nouvelle question)
            elif 'q' in line and not ('rep1' in line or 'rep2' in line):
                inside_rep2_to_q = False
    
            
            # Vérifier la présence de '#'
            if '#' in line:
                if inside_rep1_to_rep2:
                    rep1_to_rep2_sharps.append((i, line))
                    l.append(1)
                elif inside_rep2_to_q:
                    rep2_to_next_question_sharps.append((i, line))
                    l.append(2)
    
        #l=[0,0,0]

#         for i in range(3):
#             try:
#                 
#                 if "rep1" in rep1_to_rep2_sharps[1]:
#                     l[i]=1
#                 if "rep2" in rep2_to_next_question_sharps[1]:
#                     l[i]=2
#             except:
#                 a=1
        return(l)
    
    #st.write("1 : ",zone)
    #st.write("2 : ",st.session_state.zone)
    #zone=1
    if zone==1: 
        correct=analyser_sharps(notebook_content.cells[i].source)
        #st.write(correct)
    



    try : 
        text+=" \n"
        exec("q=q"+classe)
        text+=textwrap.fill(q, width=53)

        answer1_text=textwrap.fill(rep1,width=20)
  
        answer2_text=textwrap.fill(rep2,width=20)
        

        
    except:
        a=1   
        
    color = (0, 0, 0)
    
    
    # Ajouter le texte sur l'image
    try:
        draw.text(position, text, fill=color, font=font)
        draw.text([a + b for a, b in zip(answer1_position, ( -2*(len(answer1_text)%20)  ,0))], answer1_text, fill=color, font=font)
        draw.text([a + b for a, b in zip(answer2_position, ( 1*(len(answer1_text)%20) - 2*(len(answer2_text)%20) ,0))], answer2_text, fill=color, font=font)
    except:
        st.write(text)
        st.write(answer1_text)
        st.write(answer2_text)



    
    #Chargement des images  wq
    try:
        # Charger les images à insérer
        im1 = Image.open("image/" + im1).convert("RGBA")
        im2 = Image.open("image/" + im2).convert("RGBA")
        # Définir les positions d'insertion (ajuste selon ton besoin)
        im1_position = (50, 100)  # Position de im1
        im2_position = (250, 100) # Position de im2
        # Coller im1 et im2 sur image
        image.paste(im1, im1_position, im1)  # Le 3e paramètre permet de garder la transparence
        image.paste(im2, im2_position, im2)
        


    except:
        a=1
    

    # Afficher l'image avec le texte sur Streamlit
    #st.image(image, caption='Centre')

    # Utiliser le canvas pour détecter les zones cliquables
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Couleur de remplissage
        stroke_width=0,  # Largeur du trait
        stroke_color="",  # Couleur du trait
        background_image=image,  # Image de fond
        update_streamlit=True  ,
        height=image.height,
        width=image.width,
        #drawing_mode=None,
        key="canvas"
    )


    #st.write(zone)
    #st.write(responses)
    #st.write(canvas_result)
   
    # Détecter les clics dans les zones spécifiées
    if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) > 0 : #and not(st.session_state.restart)  
        #for shape in canvas_result.json_data["objects"]:
            #left, top, width, height = shape["left"], shape["top"], shape["width"], shape["height"]
            
                # Récupérer le dernier objet cliqué
        last_shape = canvas_result.json_data["objects"][-1]
        left, top, width, height = last_shape["left"], last_shape["top"], last_shape["width"], last_shape["height"]

        

    
        # Vérifier si c'est un nouveau clic
        current_click = (left, top, width, height, time())
        #ancien click existe?
        try:
            a=st.session_state.last_click[0:4] != current_click[0:4] or time()-st.session_state.last_click[4]>1
        except:
            st.session_state.last_click=[1,1,1,1,1]
            
            
            
        if (st.session_state.last_click[0:4] != current_click[0:4] or time()-st.session_state.last_click[4]>0.75) and st.session_state.last_click[4]!=1  :
            st.session_state.last_click = current_click  # Enregistrer ce clic comme le dernier
            
            
            #st.write("graph : " +str(zone))
            if zone>3:
                st.write("Problème de zone : " +str(zone))
                zone=3         
            #st.write("canvas_result : ",canvas_result.json_data["objects"][-1])
            # Vérification des zones cliquées pour les réponses
            if answer1_position[0]-100 <= left <= answer1_position[0] + 50 and answer1_position[1]-100 <= top <= answer1_position[1] + 100 and width<=100:
                #st.write("Vous avez cliqué sur Réponse 1")
                responses[zone-1]=1
                zone += 1
                #st.write("cc")
        
                
                #st.session_state.i += 1  # Passe à la question suivante de la cellule
                #st.experimental_rerun()  # Recharge la page avec la nouvelle question
            elif answer2_position[0]-50 <= left <= answer2_position[0] + 100 and answer2_position[1]-100 <= top <= answer2_position[1] + 100 and width<=100:
                #st.write("Vous avez cliqué sur Réponse 2")
                responses[zone-1]=2
                zone += 1
                #print("cc2")
                #st.session_state.i += 1  # Passe à la question suivante de la cellule
                #st.experimental_rerun()  # Recharge la page avec la nouvelle question  N'éxécute pas ce qu'il y a après
                
    
            else:
                st.write("Arrête de dessiner !")

    try:
        if st.session_state.last_click[4]==1     :
            st.session_state.last_click[4]=st.session_state.last_click[4] + 1   
    except:
        pass
        
    if st.session_state.triche==1:
        if result['brep']==1    :
            st.write("v")
        if result['brep']==2:
            #st.write("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;v", unsafe_allow_html=True)
            st.write('<p style="white-space: pre;">                                                                              v</p>', unsafe_allow_html=True)

import streamlit as st
from PIL import Image



# Chemin de l'image principale
main_image_path = "image/t4.png"

# Chemins des images à ajouter
image_vrai_path = "image/vrai.png"
image_faux_path = "image/faux.png"
#image_faux1_path = "image/faux.png"
#image_faux2_path = "image/faux.png"


#                 # Déterminer si la réponse est correcte
#                 if rep1 == "correct":  # Remplacez par la condition correcte
#                     image_vrai_path = "image/vrai.png"
#                 else:
#                     image_vrai_path = "image/faux.png"




# Positions où les images seront ajoutées
positions = [(50, 10), (50, 80), (50, 150)]  # Ajustez les positions en fonction de vos besoins



with col3:
    # Chemins des images "vrai" et "faux"
    image_vrai_path = "image/vrai.png"
    image_faux_path = "image/faux.png"
    
    #st.write(responses)

    # Liste des positions où les images seront ajoutées (max 3 images)
    positions = [(50, 15), (50, 80), (50, 150)]  # Ajustez les positions si nécessaire

    # Créer une liste d'images à ajouter en fonction des réponses (correct contient 1 ou 2)
    overlay_images = []
    for j in range(3):
        if responses[j]!=0:
            if responses[j] == correct[j]:
                overlay_images.append(image_vrai_path)
            else:
                overlay_images.append(image_faux_path)
    
    # Vérifier qu'il y a des images à afficher
    #st.write(correct)
    if len(overlay_images)>0:
        # Limiter le nombre d'images à 3 (si jamais correct contient plus de 3 éléments)
        overlay_images = overlay_images[:3]

        # Ajouter les images à l'image principale
        image_with_vrai = add_image_to_image(main_image_path, overlay_images, positions)
        
        # Afficher l'image combinée dans Streamlit
        st.image(image_with_vrai, caption='', use_column_width=True)#Images combinées
    else:
        #st.write("Aucune image à afficher.")
        image_with_vrai = Image.open(main_image_path).convert("RGBA")
        st.image(image_with_vrai, caption=' ', use_column_width=True)



# Zone de texte pour faire défiler des dialogues
st.subheader("Dialogues :")
st.text_area("Entrez votre dialogue ici", height=200)

# Zone de texte pour entrer du code
st.subheader("Codes :")
try:
    user_code = st.text_area("Entrez votre code ici", height=200,value=user_code)
except:
    user_code = st.text_area("Entrez votre code ici", height=200,value="")
st.session_state.user_code = user_code # Mettre à jour session_state si l'utilisateur modifie la zone de texte

# Bouton pour exécuter le code
if st.button("Exécuter le code"):
    try:
        # Créer un buffer pour capturer les sorties standard
        buffer = io.StringIO()
        sys.stdout = buffer  # Rediriger les sorties print vers le buffer
        # Utiliser exec pour exécuter le code entré par l'utilisateur
        exec(user_code)
        # Récupérer le contenu du buffer
        result = buffer.getvalue()
        # Afficher le résultat du code exécuté
        st.write( result, height=200)
    except Exception as e:
        # Afficher une erreur si le code n'est pas correct
        st.error(f"Erreur lors de l'exécution : {e}")
    finally:
        # Remettre sys.stdout à son état normal
        sys.stdout = sys.__stdout__







# # Chemin vers le fichier QCM.ipynb
# chemin_fichier = "QCM.ipynb"
# 
# # Charger le contenu du fichier
# with open(chemin_fichier, "r", encoding='utf-8') as f:
#     notebook_content = nbf.read(f, as_version=4)
# premiere_cellule = notebook_content.cells[0]
# st.write(premiere_cellule.source)
# st.write("q6" in premiere_cellule.source)
# st.write("q5" in premiere_cellule.source)
# st.write(premiere_cellule.source[0:1000])
# st.write("#" in premiere_cellule.source[premiere_cellule.source.find("rep1"):premiere_cellule.source.find("rep2")])





st.session_state.i=i
#st.session_state.zone=zone
st.session_state.correct=correct
st.session_state.classe=classe 
st.session_state.responses=responses

# Attendre 1 seconde
#sleep(1)


st.session_state.restart=0
# Ajout du bouton "Restart"
if st.button("Restart"):
    # Supprime la variable `zone` de la session si elle existe
    print("restart")
    del st.session_state["zone"]
    st.session_state.last_click=[1,1,1,1,1]
    st.session_state.restart=1
    # Relancer l'application pour appliquer les changements
    st.experimental_rerun()


#Maj Question
if st.session_state.zone!=zone:
    st.session_state.zone=zone
    st.experimental_rerun()
st.session_state.zone=zone





if 0==1:#pour mettre en transparent le blanc d'une image
    # Chemin de l'image d'origine et de l'image de sortie
    image_path = "image/X.png"
    output_path = image_path    #"image/X.png"
        
    from PIL import Image
    
    def replace_white_with_transparency(image_path, output_path):
        # Ouvrir l'image
        img = Image.open(image_path).convert("RGBA")
    
        # Obtenir les données de l'image
        datas = img.getdata()
    
        # Créer une nouvelle liste pour stocker les données modifiées
        new_data = []
    
        for item in datas:
            # Remplacer les pixels blancs par des pixels transparents
            # Comparer la valeur RGB du pixel (255, 255, 255) pour le blanc
            if item[:3] == (255, 255, 255):
                # Ajouter un pixel transparent
                new_data.append((255, 255, 255, 0))
            else:
                # Ajouter le pixel d'origine
                new_data.append(item)
    
        # Mettre à jour les données de l'image avec les nouvelles données
        img.putdata(new_data)
    
        # Enregistrer l'image modifiée
        img.save(output_path, "PNG")
        
    # Remplacer le blanc par du transparent
    replace_white_with_transparency(image_path, output_path)
    
    # Afficher l'image modifiée
    #img = Image.open(output_path)
    #img.show()