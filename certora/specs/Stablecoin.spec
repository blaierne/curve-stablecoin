methods {
    function totalSupply() external returns uint256 envfree;
    function minter() external returns address envfree;
}

ghost mathint sum_of_balances {
    init_state axiom sum_of_balances == 0;
}

hook Sstore balanceOf[KEY address user] uint256 newvalue (uint256 oldvalue) STORAGE {
    sum_of_balances = sum_of_balances + newvalue - oldvalue;
}

invariant totalSupplyEqualsSum()
    to_mathint(totalSupply()) == sum_of_balances;

rule onlyMintCanIncreaseSupply() {
    method f;
    calldataarg args;
    env e;

    uint256 supplyBefore = totalSupply();
    f(e, args);
    uint256 supplyAfter = totalSupply();

    assert supplyAfter > supplyBefore =>
        (f.selector == sig:mint(address, uint256).selector
         && e.msg.sender == minter());
}

rule sanity(method f, calldataarg args, env e) {
    f(e,args);

    satisfy(true);
}
