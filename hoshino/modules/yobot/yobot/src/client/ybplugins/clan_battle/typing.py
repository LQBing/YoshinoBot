from dataclasses import dataclass
from typing import Any, Dict, List, NewType, Optional

Pcr_date = NewType('Pcr_date', int)
Pcr_time = NewType('Pcr_time', int)
QQid = NewType('QQid', int)
Groupid = NewType('Groupid', int)



@dataclass
class BossChallenge:
    date: Pcr_date
    time: Pcr_time
    cycle: int
    num: int
    health_remain: int
    damage: int
    is_continue: bool
    team: Optional[List[int]]
    message: Optional[str]


ClanBattleReport = NewType(
    'ClanBattleReport',
    List[Dict[str, Any]]
)
