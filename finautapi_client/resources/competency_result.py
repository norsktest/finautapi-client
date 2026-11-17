"""Competency result resource for FinAut API client.

A competency result is a completed course from an external system (an LMS)
registered against a goal in FinAut. The user is identified by the
encrypted user id the LMS got from the FinAut-login flow (get-user-id).
"""

import datetime
from typing import Dict, Any, Optional, Union


def _isodate(value):
    """'YYYY-MM-DD' for a date or datetime; anything else unchanged."""
    if isinstance(value, datetime.datetime):
        value = value.date()
    if isinstance(value, datetime.date):
        return value.isoformat()
    return value


class CompetencyResultResource:
    """Handle competency result-related API operations."""

    def __init__(self, client):
        """Initialize competency result resource with API client."""
        self.client = client
        self.endpoint = "competency_result"

    def _link(self, endpoint: str, value: Union[int, str]) -> str:
        """Return the hyperlink the API expects for a related object.

        Accepts an id (``12`` or ``"12"``) or a full URL, which is passed
        through unchanged.
        """
        value = str(value)
        if value.startswith(("http://", "https://")):
            return value
        return f"{self.client.base_url}{endpoint}/{value}/"

    def list(
        self,
        encoded_userid: Optional[str] = None,
        persnr: Optional[str] = None,
        employee_alias: Optional[str] = None,
        goal: Optional[Union[int, str]] = None,
        from_date: Optional[Union[str, datetime.date]] = None,
        page: Optional[int] = None,
        encrypted_userid: Optional[str] = None,
    ) -> Any:
        """
        List competency results for your subordinates.

        Args:
            encoded_userid: Encrypted user id (from FinAut-login) of one user
            persnr: Norwegian national identity number of one user
            employee_alias: Your company's identifier for one user
            goal: Goal id (e.g. 12) or goal code (e.g. 'LIKOFF26')
            from_date: Only results finished on or after this date
                (YYYY-MM-DD). ``finished`` is the completion date, not the
                registration date, so fetch with an overlap and de-duplicate
                on ``id``.
            page: Page number, where the API paginates
            encrypted_userid: Deprecated alias for ``encoded_userid``

        Returns:
            The decoded JSON response (a list, or a paginated dictionary
            where the host paginates)
        """
        encoded_userid = encoded_userid or encrypted_userid
        params = {
            'encoded_userid': encoded_userid,
            'persnr': persnr,
            'employee_alias': employee_alias,
            'goal': goal,
            'from_date': _isodate(from_date),
            'page': page,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return self.client.get(f"{self.endpoint}/", params=params)

    def get(self, result_id: int) -> Dict[str, Any]:
        """
        Get a specific competency result by ID.

        Args:
            result_id: Result ID

        Returns:
            Competency result details dictionary
        """
        return self.client.get(f"{self.endpoint}/{result_id}/")

    def create(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new competency result from a raw payload.

        All fields are required:
            - goal: URL of the goal, e.g. '.../finautapi/v1/goals/12/'
            - reward_type: URL of the reward type,
              e.g. '.../finautapi/v1/reward_types/3/'
            - user: Encrypted user id from FinAut-login
            - finished: Completion date, 'YYYY-MM-DD'
            - courseinfo: Course name/description (max 200 characters)
            - content_responsible: Who is responsible for the course
              content (max 120 characters)
            - value: How much the course counts towards the goal
            - external_system: Name of your LMS (max 100 characters)
            - external_id: The completion's id in your LMS (max 80
              characters)

        The same external_system + external_id + goal is registered only
        once: posting it again raises FinAutAPIException (status_code 400,
        "must make a unique set"), so a retry is safe. If a course covers
        several goals, post once per goal with the same external_id.

        Prefer :meth:`record_completion`, which builds the links for you.

        Returns:
            Created competency result details
        """
        return self.client.post(f"{self.endpoint}/", json=result_data)

    def record_completion(
        self,
        encrypted_userid: str,
        *,
        goal: Union[int, str],
        reward_type: Union[int, str],
        finished: Union[str, datetime.date],
        value: float,
        courseinfo: str,
        content_responsible: str,
        external_system: str,
        external_id: str,
    ) -> Dict[str, Any]:
        """
        Record that a user completed a course counting towards a goal.

        Args:
            encrypted_userid: Encrypted user id from FinAut-login
            goal: Goal id or URL (see ``client.get('goals/')``)
            reward_type: Reward type id or URL
                (see ``client.get('reward_types/')``)
            finished: Completion date (date or 'YYYY-MM-DD')
            value: How much the course counts towards the goal
            courseinfo: Course name/description
            content_responsible: Who is responsible for the course content
            external_system: Name of your LMS
            external_id: The completion's id in your LMS

        Returns:
            Created competency result details

        Example:
            client.competency_results.record_completion(
                'N3F2A...',
                goal=12,
                reward_type=3,
                finished='2026-11-16',
                value=2,
                courseinfo='Etikk og god skikk 2026',
                content_responsible='Kari Nordmann',
                external_system='MyLMS',
                external_id='completion-4711',
            )
        """
        return self.create({
            "user": encrypted_userid,
            "goal": self._link("goals", goal),
            "reward_type": self._link("reward_types", reward_type),
            "finished": _isodate(finished),
            "value": value,
            "courseinfo": courseinfo,
            "content_responsible": content_responsible,
            "external_system": external_system,
            "external_id": external_id,
        })
