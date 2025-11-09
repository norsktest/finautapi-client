"""Resource modules for FinAut API client."""

from .users import UserResource
from .companies import CompanyResource
from .departments import DepartmentResource
from .userstatus import UserStatusResource
from .results import ResultResource
from .competency_result import CompetencyResultResource
from .employment import EmploymentResource

__all__ = [
    "UserResource",
    "CompanyResource",
    "DepartmentResource",
    "UserStatusResource",
    "ResultResource",
    "CompetencyResultResource",
    "EmploymentResource",
]