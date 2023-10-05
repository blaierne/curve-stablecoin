using AMM as AMM;

methods {
    function AMM._p_oracle_up(int256 x) external returns (uint256) => P_Oracle_Up_CVL(x);
    function AMM._price_oracle_ro() external returns (uint256[2]);
    function AMM.p_oracle_up(int256) external returns (uint256) envfree;
}

function P_Oracle_Up_CVL(int256 x) returns uint256 {
    uint256 abs_x = x > 0 ? require_uint256(x) : require_uint256(0-x); 
    return require_uint256(2 * abs_x);
}

rule test_summary() {
    satisfy AMM.p_oracle_up(2) == 4;
}