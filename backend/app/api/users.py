from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.user import (
    FilenameSuccessOut,
    LocalDataImportRequest,
    UserDataMutationOut,
    UserDataOut,
    UserEventRequest,
)
from app.services import user_data as user_data_service

router = APIRouter(prefix="/me")


@router.get("/data", response_model=UserDataOut)
def get_my_data(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> UserDataOut:
    return user_data_service.serialize_user_data(db, user)


@router.put("/favorites/{filename}", response_model=FilenameSuccessOut)
def add_favorite(
    filename: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> FilenameSuccessOut:
    user_data_service.add_favorite(db, user, filename)
    return FilenameSuccessOut(filename=filename)


@router.delete("/favorites/{filename}", response_model=FilenameSuccessOut)
def remove_favorite(
    filename: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> FilenameSuccessOut:
    user_data_service.remove_favorite(db, user, filename)
    return FilenameSuccessOut(filename=filename)


@router.put("/collection/{filename}", response_model=FilenameSuccessOut)
def add_collection(
    filename: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> FilenameSuccessOut:
    user_data_service.add_collection(db, user, filename)
    return FilenameSuccessOut(filename=filename)


@router.post("/import-local-data", response_model=UserDataMutationOut)
def import_local_data(
    payload: LocalDataImportRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserDataMutationOut:
    data = user_data_service.import_local_data(db, user, payload)
    return UserDataMutationOut(data=data)


@router.post("/events", response_model=UserDataMutationOut)
def track_event(
    payload: UserEventRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserDataMutationOut:
    data = user_data_service.track_event(db, user, payload)
    return UserDataMutationOut(data=data)
