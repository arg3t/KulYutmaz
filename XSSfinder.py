suspiciusLetters = ["<",">","|",";","%"] # Buraya birkaç karakter daha eklemek gerekebilir.

def XSSsearcher(url): # Bu algoritma kolay olsada iyi çalışıyor gibi duruyor. (DOM için çalışıyor sadece)
    for letter in url:
        if letter in suspiciusLetters:
            return True
    return False


