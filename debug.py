import torch

print(torch.cuda.is_available())  # Dovrebbe restituire True se la GPU è disponibile
print(torch.cuda.current_device())  # Restituisce l'indice della GPU corrente
print(torch.cuda.get_device_name(0))