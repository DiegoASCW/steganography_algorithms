#
# funções de suporte para codificação do mét. Aditivo
#


import cv2
import numpy as np


def extract_pixels(img) -> 0b0 :
    """
    Retorna os bytes da imagem
    """

    rows, cols, _ = img.shape
    
    pixels_list = []

    for i in range(rows):
        for j in range(cols):
            pixels_list.append(img[i,j].tolist())

    return pixels_list


def modify_byte(byte_original: int, bit: int, fator_w: int) -> int:
    """
    Modifica um byte usando o método aditivo.

    h' = h + (bit * w)
    """
    novo_byte = byte_original + (bit * fator_w)
    novo_byte_clamped = max(0, min(255, novo_byte))
    
    return novo_byte_clamped


def image_construct(pixels_list: list, height: int, width: int, output_img_path: str) -> None:
    """
    Reconstrói uma imagem a partir de uma lista plana de pixels e das dimensões originais
    """
    if not pixels_list or height <= 0 or width <= 0:
        print("A lista de pixels está vazia ou as dimensões são inválidas.")
        return 
    
    try:
        # converte lista para um array NumPy (dtype=np.uint8)
        flat_array = np.array(pixels_list, dtype=np.uint8)
        
        channels = 3

        # valida se o array passado está de acordo com o esperado        
        expected_size = height * width * channels
        if flat_array.size != expected_size:
            raise ValueError(
                f"Tamanho do array ({flat_array.size}) não corresponde às dimensões fornecidas "
                f"({height}x{width}x{channels} = {expected_size})."
            )

        reconstructed_img = flat_array.reshape((height, width, channels))
        cv2.imwrite(output_img_path, reconstructed_img)

        print(f"Imagem salva: {output_img_path}. Dimensões: {reconstructed_img.shape}")

    except Exception as e:
        print(f"ERRO durante a reconstrução: {e}")
        