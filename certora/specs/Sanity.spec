methods {
//    function _.ext_p_oracle_up(int256) external => NONDET;
}

//ghost p_oracle_summary(int256) returns uint256;

rule sanity(method f, calldataarg args, env e) {
    f(e,args);

    satisfy(true);
}
