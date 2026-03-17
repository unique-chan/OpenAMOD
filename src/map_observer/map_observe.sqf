// Copy & paste to ARMA3
// After run, check recent `arma*.RPT` in C:\Users\{your_pc_user_name}\AppData\Local\Arma 3 !

checkMapLandAndWater = {
    private _mapSize = worldSize;
    private _step = 100;
    private _landPositions = [];
    private _waterPositions = [];

    for "_x" from 0 to _mapSize step _step do {
        for "_y" from 0 to _mapSize step _step do {
            private _position = [_x, _y];
            if (surfaceIsWater _position) then {
                _waterPositions pushBack _position;
            } else {
                _landPositions pushBack _position;
            };
        };
    };

    [_landPositions, _waterPositions]
};

_result = call checkMapLandAndWater;
_landPositions = _result select 0;
_waterPositions = _result select 1;

diag_log "-> start";
diag_log worldName;

diag_log format [""];
{
    diag_log format ["Land Position: %1", _x];
} forEach _landPositions;
diag_log "SEA";
{
    diag_log format ["Water Position: %1", _x];
} forEach _waterPositions;

diag_log "-> end";
