from fastapi import APIRouter, Query

from app.common.response import ApiResponse
from app.dependencies.services import IssueServiceDep
from app.schemas.issue import IssueResponse


router = APIRouter(
    prefix="/issues",
    tags=["issues"],
)


@router.get(
    "",
    response_model=ApiResponse[list[IssueResponse]],
)
async def get_issues(
    issue_service: IssueServiceDep,
    limit: int = Query(
        default=3,
        ge=1,
        le=10,
    ),
) -> ApiResponse[list[IssueResponse]]:

    result = await issue_service.get_recent_issues(
        limit=limit
    )

    return ApiResponse(
        success=True,
        data=result,
        error=None,
    )


@router.get(
    "/{issue_id}",
    response_model=ApiResponse[IssueResponse],
)
async def get_issue(
    issue_id: int,
    issue_service: IssueServiceDep,
) -> ApiResponse[IssueResponse]:

    result = await issue_service.get_issue(
        issue_id
    )

    return ApiResponse(
        success=True,
        data=result,
        error=None,
    )