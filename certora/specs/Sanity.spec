methods {
    function AMM._p_oracle_up(int256 n) internal returns uint256 => p_oracle_summary(n);
}

ghost p_oracle_summary(int256) returns uint256;

rule sanity(method f, calldataarg args, env e) {
    f(e,args);

    satisfy(true);
}
