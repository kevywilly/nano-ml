from typing import Any

from pydantic import BaseModel


class CameraModel(BaseModel):
    M1: Any
    M2: Any
    dist1: Any
    dist2: Any
    rvecs1: Any
    rvecs2: Any
    R: Any
    T: Any
    E: Any
    F: Any
