#
#   Avaliação Somativa 2 | Data Hiding
# 
# Diego Lautenschlager, Lincoln Felix
#

# ex de esconder
# python3 run.py --hide  -i ../Images/PUCPR.png -s ../Images/esconderLogo.png -o ../Images/SAIDA.png -a 2

# ex de extração
# python3 run.py -i ../Images/PUCPR.png -s ../Images/esconderLogo.png  -w ../Images/SAIDA.png  -o imagemExtraida.png -a 2
                                                                             

import cv2
import argparse
from os import _exit
from pathlib import Path

from encoder_module import *
from decoder_module import *


def encode(target_img_path: str, secret_img_path: str, output_img_path: str, fator_escala: str) -> None:
    """
    Esconde uma imagem na outra
    """

    target_img = cv2.imread(target_img_path)
    secret_img = cv2.imread(secret_img_path)

    target_height, target_width, target_channels = target_img.shape
    secret_height, secret_width, secret_channels = secret_img.shape
    
    print(f"Dimensões da imagem ORIGINAL: Altura {target_height}  -  Largura {target_width}  -  Canais {target_channels}")
    print(f"Dimensões da imagem SECRETA: Altura {secret_height}  -  Largura {secret_width}  -  Canais {secret_channels}")

    # verifica se é possível esconder a imagem
    if not (target_img.nbytes / 8 > secret_img.nbytes):
        print(f"ERRO: Não é possível esconder a imagem '{secret_img_path}' na imagem '{target_img_path}' ...")
        _exit(1)

    # extrai os pixels das imagens de entrada
    target_img_pixels: list = extract_pixels(target_img)
    secret_img_pixels: list = extract_pixels(secret_img)

    # coleta os bits da imagem secreta
    def get_secret_bits():
        for pixel in secret_img_pixels:
            for channel in pixel:
                for bit in f'{channel:08b}':
                    yield int(bit)

    secret_bit_generator = get_secret_bits()
    new_target_pixels = []

    # sinaliza se todos os bits secretos foram escondidos
    flag_zero = False

    # itera sobre a imagem de cobertura
    for pixel in target_img_pixels:
        
        # se todos os bits secretos já foram escondidos,
        #   adiciona todos os originais sem alteração
        if flag_zero:
            new_target_pixels.append(pixel) 
            continue

        new_pixel = pixel

        # modifica os três canais RGB
        for i in range(3):
            try:
                # avança o próx bit secreto
                secret_bit = next(secret_bit_generator)

                # modifica o canal alvo
                original_channel_value = pixel[i]
                new_channel_value = modify_byte(original_channel_value, secret_bit, int(fator_escala))
                new_pixel[i] = new_channel_value

            except StopIteration:
                flag_zero = True
                break

        new_target_pixels.append(tuple(new_pixel))

    # salva imagem
    image_construct(new_target_pixels, target_height, target_width, output_img_path)


def decode(target_img_path: str, secret_img_path: str, watermark_img_path: str, output_img_path: str, fator_escala: str) -> None:
    """
    Extrai a imagem secreta
    """

    target_img = cv2.imread(target_img_path)
    secret_img = cv2.imread(secret_img_path)
    watermark_img = cv2.imread(watermark_img_path)

    secret_height, secret_width, secret_channels = secret_img.shape
    w_int = int(fator_escala)
    
    # verifica quantidade esperada de bits a serem alterados
    total_bits_necessarios = secret_height * secret_width * secret_channels * 8
    print(f"Tentando extrair {total_bits_necessarios} bits...")

    # extrai os pixels das imagens de entrada
    target_img_pixels: list = extract_pixels(target_img)
    watermark_img_pixels: list = extract_pixels(watermark_img)

    extracted_bits = []
    
    pixel_iterator_img_codificada = iter(target_img_pixels)
    pixel_iterator_watermark = iter(watermark_img_pixels)

    ## extrai os bits da watermark
    while len(extracted_bits) < total_bits_necessarios:
        pixel_h = next(pixel_iterator_img_codificada)
        pixel_h_prime = next(pixel_iterator_watermark)

        # interage sobre os 3 canais de cor RGB
        for i in range(3): 
            
            # quebra o loop se já coletamos a qntd prevista da watermark
            if len(extracted_bits) >= total_bits_necessarios:
                break
                
            original_val = pixel_h[i]
            modified_val = pixel_h_prime[i]
            
            # extrai o bit e o adiciona à lista
            extracted_bit = extract_hidden_bit(original_val, modified_val, w_int)
            extracted_bits.append(extracted_bit)
        
    new_secret_pixels = []
    
    # converte a lista de bits em um iterador
    bit_iterator = iter(extracted_bits)
    
    total_pixels_necessarios = secret_height * secret_width

    ## re-ordena os bits para formar os canais originais    
    for _ in range(total_pixels_necessarios):
        pixel_channels = [] 
        
        for _ in range(3):
            byte_bits = [next(bit_iterator) for _ in range(8)]

            # converte de lista -> string
            # [1,0,1,1,...] -> "1011..."
            byte_str = "".join(map(str, byte_bits))

            # Converte a string de bits em um inteiro (valor do canal)
            channel_value = int(byte_str, 2)
            pixel_channels.append(channel_value)
        
        new_secret_pixels.append(tuple(pixel_channels))

    # salva a imagem
    image_construct(new_secret_pixels, secret_height, secret_width, output_img_path)


def main() -> None:
    PARSER = argparse.ArgumentParser(prog='Least Significant Bit')
    PARSER.add_argument('-i', '--input-img', required=True, help='Caminho absoluto da imagem que você quer esconder alguma informação')
    PARSER.add_argument('-o', '--output-img', help='Caminho absoluto de onde você quer salvar a imagem com uma informação escondida')
    PARSER.add_argument('-s', '--secret-img', help='Imagem à ser escondida na imagem')
    PARSER.add_argument('-w', '--watermark-img', help='Imagem de marca dagua. USAR SEM O HIDE')
    PARSER.add_argument('-a', '--fator-escala', help='Fator de escala')
    PARSER.add_argument('--hide', help='Flag para indicar se você quer esconder ou revelar uma mensagem de uma imagem', action=argparse.BooleanOptionalAction)
    PARSER.set_defaults(hide=False)

    args = PARSER.parse_args()

    if args.hide == True:
        encode(Path(args.input_img), Path(args.secret_img), Path(args.output_img), args.fator_escala)
    else:
        decode(Path(args.input_img), Path(args.secret_img), Path(args.watermark_img), Path(args.output_img), args.fator_escala)


if __name__ == "__main__":
    main()
