"""SkipTrace public records search tool."""

from backend.tools.base import BaseTool, ToolResult


class SkipTraceTool(BaseTool):
    @property
    def name(self) -> str:
        return "skiptrace_search"

    @property
    def description(self) -> str:
        return (
            "Searches public records for person, business, or property information. "
            "Use this tool when the user asks to find or locate a person, business, or property. "
            "Results are for legally permissible purposes only under FCRA/DPPA."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "full_name": {
                    "type": "string",
                    "description": "Full name of the person or business entity to search for.",
                },
                "state": {
                    "type": "string",
                    "description": "US state abbreviation (e.g. 'TX', 'CA') to narrow the search.",
                },
                "city": {
                    "type": "string",
                    "description": "City name to narrow the search.",
                },
                "date_of_birth": {
                    "type": "string",
                    "description": "Date of birth in YYYY-MM-DD format.",
                },
                "search_type": {
                    "type": "string",
                    "enum": ["person", "business", "property"],
                    "description": "Type of record to search for. Defaults to 'person'.",
                },
            },
            "required": ["full_name"],
        }

    async def execute(self, **kwargs) -> ToolResult:
        full_name = kwargs.get("full_name", "").strip()
        if not full_name:
            return ToolResult(
                tool_name=self.name,
                success=False,
                data={},
                error="full_name is required",
            )

        state = kwargs.get("state")
        city = kwargs.get("city")
        date_of_birth = kwargs.get("date_of_birth")
        search_type = kwargs.get("search_type", "person")

        results = await self._search_public_records(
            full_name=full_name,
            state=state,
            city=city,
            date_of_birth=date_of_birth,
            search_type=search_type,
        )

        disclaimer = (
            "FCRA/DPPA NOTICE: This information is provided for legally permissible purposes only. "
            "Use is restricted to permissible purposes under the Fair Credit Reporting Act (FCRA) "
            "and the Driver's Privacy Protection Act (DPPA)."
        )

        return ToolResult(
            tool_name=self.name,
            success=True,
            data={
                "query": {
                    "full_name": full_name,
                    "state": state,
                    "city": city,
                    "date_of_birth": date_of_birth,
                    "search_type": search_type,
                },
                "results": results,
                "disclaimer": disclaimer,
            },
        )

    async def _search_public_records(
        self,
        full_name: str,
        state: str | None,
        city: str | None,
        date_of_birth: str | None,
        search_type: str,
    ) -> list[dict]:
        """Stub: integrate with a real public-records API such as TLO, Tracers, or BeenVerified."""
        return [
            {
                "message": (
                    "Public records search is not yet connected to a live data provider. "
                    "To activate, integrate with a permissible-purpose API such as TLO, "
                    "Tracers Info, or BeenVerified and replace this stub."
                ),
                "full_name": full_name,
                "state": state,
                "city": city,
                "date_of_birth": date_of_birth,
                "search_type": search_type,
                "records": [],
            }
        ]
