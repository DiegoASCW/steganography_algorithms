#
# funções de suporte para decodificação do mét. Aditivo
#


def extract_hidden_bit(original_channel_val: int, modified_channel_val: int, fator_w: int) -> int:
    """
    Extrai um bit escondido (0 ou 1) comparando o canal original (h)
    com o canal modificado (h').

    h' = h + (bit * w)
    """
    diferenca = int(modified_channel_val) - int(original_channel_val)
    limite = fator_w / 2

    return 1 if diferenca >= limite else 0
