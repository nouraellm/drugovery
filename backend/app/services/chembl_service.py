import httpx
from typing import Optional, Dict, Any
from app.core.config import settings


async def search_chembl_compound(smiles: str) -> Optional[Dict[str, Any]]:
    """Search for compound in ChEMBL by SMILES"""
    try:
        async with httpx.AsyncClient() as client:
            # ChEMBL API endpoint for similarity search
            url = f"{settings.CHEMBL_API_URL}/similarity/{smiles}/100"
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                if data.get("molecules"):
                    # Return first match
                    molecule = data["molecules"][0]
                    return {
                        "external_id": molecule.get("molecule_chembl_id"),
                        "external_source": "chembl",
                        "name": molecule.get("pref_name") or molecule.get("molecule_chembl_id"),
                        "properties": {
                            "alogp": molecule.get("alogp"),
                            "molecular_weight": molecule.get("molecular_weight"),
                            "num_ro5_violations": molecule.get("num_ro5_violations"),
                        }
                    }
    except Exception as e:
        print(f"Error searching ChEMBL: {e}")
    return None


async def get_chembl_compound_by_id(chembl_id: str) -> Optional[Dict[str, Any]]:
    """Get compound details from ChEMBL by ID"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{settings.CHEMBL_API_URL}/molecule/{chembl_id}"
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                return {
                    "external_id": data.get("molecule_chembl_id"),
                    "external_source": "chembl",
                    "name": data.get("pref_name") or data.get("molecule_chembl_id"),
                    "smiles": data.get("molecule_structures", {}).get("canonical_smiles"),
                    "properties": {
                        "alogp": data.get("alogp"),
                        "molecular_weight": data.get("molecular_weight"),
                        "num_ro5_violations": data.get("num_ro5_violations"),
                    }
                }
    except Exception as e:
        print(f"Error fetching ChEMBL compound: {e}")
    return None
