from fastapi import APIRouter
import yaml
from ..config import SCOF_PROFILE_PATH
import os

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/active")
async def get_active_profile():
    profile_file = os.path.join(SCOF_PROFILE_PATH, "profile.yaml")
    try:
        with open(profile_file, "r") as f:
            profile_data = yaml.safe_load(f)
            
        return {
            "metadata": profile_data.get("meta", {}),
            "agent_count": len(profile_data.get("agents", [])),
            "disruption_type_count": len(profile_data.get("scenarios", {}).get("disruption_types", [])),
            "entity_summary": {
                "suppliers": len(profile_data.get("domain", {}).get("entities", {}).get("suppliers", [])),
                "facilities": len(profile_data.get("domain", {}).get("entities", {}).get("facilities", []))
            }
        }
    except Exception as e:
        return {"error": f"Failed to load profile: {e}"}
