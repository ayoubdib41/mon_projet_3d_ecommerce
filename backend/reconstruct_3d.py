import os
import subprocess
import shutil
import struct
import json

# --- CONFIGURATION MESHROOM ---
# Sur TON PC : Laisse "meshroom_batch" (ça ne marchera pas mais fera le cube de test)
# Sur le PC DE TON AMI : Il doit mettre le chemin complet vers meshroom_batch.exe
# Exemple : MESHROOM_EXECUTABLE = r"C:\Meshroom-2023.1.0\meshroom_batch.exe"
MESHROOM_EXECUTABLE = "meshroom_batch" 

def create_simple_glb(output_path):
    # Données d'un cube très simple
    pos = [-0.5,-0.5,0.5, 0.5,-0.5,0.5, 0.5,0.5,0.5, -0.5,0.5,0.5, -0.5,-0.5,-0.5, 0.5,-0.5,-0.5, 0.5,0.5,-0.5, -0.5,0.5,-0.5]
    ind = [0,1,2, 0,2,3, 7,4,5, 7,5,6, 1,0,4, 1,4,5, 2,1,5, 2,5,6, 3,2,6, 3,6,7, 0,3,7, 0,7,4]
    
    pos_b = struct.pack(f'{len(pos)}f', *pos)
    ind_b = struct.pack(f'{len(ind)}H', *ind)

    gltf = {
        "asset": {"version": "2.0"},
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1}]}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": 8, "type": "VEC3", "max": [0.5,0.5,0.5], "min": [-0.5,-0.5,-0.5]},
            {"bufferView": 1, "componentType": 5123, "count": 36, "type": "SCALAR"}
        ],
        "bufferViews": [
            {"buffer": 0, "byteLength": len(pos_b), "target": 34962},
            {"buffer": 0, "byteOffset": (len(pos_b) + 3) & ~3, "byteLength": len(ind_b), "target": 34963}
        ],
        "buffers": [{"byteLength": (len(pos_b) + 3) & ~3 + len(ind_b)}]
    }

    json_d = json.dumps(gltf, separators=(',', ':')).encode('utf-8')
    json_p = json_d + b' ' * ((4 - (len(json_d) % 4)) % 4)
    bin_p = pos_b + b'\0' * ((4 - (len(pos_b) % 4)) % 4) + ind_b
    bin_p += b'\0' * ((4 - (len(bin_p) % 4)) % 4)

    with open(output_path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(json_p) + 8 + len(bin_p)))
        f.write(struct.pack('<II', len(json_p), 0x4E4F534A))
        f.write(json_p)
        f.write(struct.pack('<II', len(bin_p), 0x004E4942))
        f.write(bin_p)
        
def run_3d_reconstruction(image_paths, output_folder, product_id):
    """Tente Meshroom, sinon fait un cube de simulation."""
    input_dir = os.path.dirname(image_paths[0])
    # Meshroom travaille mieux avec des chemins absolus
    abs_input_dir = os.path.abspath(input_dir)
    abs_output_folder = os.path.abspath(output_folder)
    
    # On définit le nom du fichier de sortie
    # Note: Meshroom sort du .obj, model-viewer préfère le .glb
    # Pour le test, on va rester sur le format que l'on génère
    output_path = os.path.join(abs_output_folder, f"{product_id}.glb")

    print(f"--- Démarrage de la tâche : {product_id} ---")

    # 1. Tenter la vraie reconstruction (si Meshroom est présent)
    if shutil.which(MESHROOM_EXECUTABLE) or os.path.exists(MESHROOM_EXECUTABLE):
        try:
            print("Exécution de Meshroom... Cela peut être long.")
            # Commande simplifiée pour Meshroom
            subprocess.run([
                MESHROOM_EXECUTABLE, 
                "--input", abs_input_dir, 
                "--output", abs_output_folder
            ], check=True)
            # Si Meshroom sort un fichier, on le retourne
            # (Attention: Meshroom sort souvent texturedMesh.obj, il faudra le renommer ici)
            return output_path 
        except Exception as e:
            print(f"Meshroom a échoué ou n'est pas configuré : {e}")
    
    # 2. Simulation (pour ton PC de dev)
    print("Mode Simulation : Création d'un cube 3D.")
    create_simple_glb(output_path)
    return output_path