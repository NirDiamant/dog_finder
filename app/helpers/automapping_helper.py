from app.automapper import mapper
from app.DAL.models import Dog, DogImage, PossibleDogMatch
from app.DTO.dog_dto import DogDTO, DogImageDTO, PossibleDogMatchDTO
from app.viewmodels.dog_viewmodel import DogResponse, DogImageResponse, PossibleDogMatchResponse, PossibleDogMatchRequest
from app import viewmodel_mapper

def setup_mapping():
    # Define the mappings between the models and the DTOs
    mapper.add(Dog, DogDTO) #, fields_mapping={ "possibleMatch": None, "dog": None })
    mapper.add(DogDTO, Dog)
    mapper.add(DogImage, DogImageDTO)
    mapper.add(DogImageDTO, DogImage)
    mapper.add(PossibleDogMatch, PossibleDogMatchDTO, fields_mapping={ "possibleMatches": [] })
    mapper.add(PossibleDogMatchDTO, PossibleDogMatch)

    # Define the mappings between the viewmodels and the DTOs
    viewmodel_mapper.add(DogDTO, DogResponse)
    viewmodel_mapper.add(DogImageDTO, DogImageResponse)
    viewmodel_mapper.add(PossibleDogMatchDTO, PossibleDogMatchResponse)
    viewmodel_mapper.add(PossibleDogMatchRequest, PossibleDogMatchDTO)
