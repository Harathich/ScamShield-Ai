from pydantic import BaseModel, HttpUrl


class ReputationRequest(BaseModel):
    """
    Request model for Reputation Agent.
    """

    url: HttpUrl