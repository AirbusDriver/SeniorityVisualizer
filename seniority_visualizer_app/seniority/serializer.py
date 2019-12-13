from typing import Dict, Any, Type


from seniority_visualizer_app.shared.serializers import BaseSerializer
from .entities import SeniorityList, Pilot


class PilotSerializer(BaseSerializer):
    def to_dict(self, obj: Pilot) -> Dict[str, Any]:
        return {
            "employee_id": obj.employee_id,
            "hire_date": obj.hire_date,
            "retire_date": obj.retire_date,
            "literal_seniority_number": obj.literal_seniority_number,
        }


class SeniorityListSerializer(BaseSerializer):
    pilot_serializer = PilotSerializer()

    def to_dict(self, obj: SeniorityList) -> Dict[str, Any]:
        pilot_data = [self.pilot_serializer.to_dict(p) for p in obj.sorted_pilot_data]

        return {"pilots": pilot_data}


def get_serializer(obj: Any) -> Type[BaseSerializer]:
    """Get a serializer for a class or instance. Raise ValueError if one does not exists."""
    serializers = {SeniorityList: SeniorityListSerializer, Pilot: PilotSerializer}

    try:
        return serializers[obj]
    except KeyError:
        try:
            return serializers[type(obj)]
        except KeyError:
            raise ValueError(f"no serializer exists for {type(obj)}")

