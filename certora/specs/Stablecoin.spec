methods {
    function _approve(address, address, uint256) internal; // acually internal
    function _burn(address, uint256) internal;
    function _transfer(address, address, uint256) internal;
    function transferFrom(address, address, uint256) external returns (bool);
    function transfer(address, uint256) external returns (bool);
    function approve(address, uint256) external returns (bool);
    function permit(address, address, uint256, uint256, uint8, bytes32, bytes32) external returns (bool);
    function increaseAllowance(address, uint256) external returns (bool);
    function decreaseAllowance(address, uint256) external returns (bool);
    function burnFrom(address, uint256) external returns (bool);
    function burn(uint256) external returns (bool);
    function mint(address, uint256) external returns (bool);
    function set_minter(address) external;

    // Getters: 
    // function allowance(address, address) external returns (uint256) envfree;
    function balanceOf(address) external returns (uint256) envfree;
    function totalSupply() external returns (uint256) envfree;
}

ghost mathint sum_of_balances {
    init_state axiom sum_of_balances == 0;
}

hook Sstore balanceOf[KEY address user] uint256 newvalue (uint256 oldvalue) STORAGE {
    sum_of_balances = sum_of_balances + newvalue - oldvalue;
}

invariant totalSupplyEqualsSum()
    to_mathint(totalSupply()) == sum_of_balances;

function doesntChangeBalance(method f) returns bool {
    return f.selector != sig:transfer(address,uint256).selector &&
        f.selector != sig:transferFrom(address,address,uint256).selector &&
        f.selector != sig:mint(address,uint256).selector &&
        f.selector != sig:burn(uint256).selector &&
        f.selector != sig:burnFrom(address,uint256).selector;
}

/*
    @Rule


    @Description:
        Verify that there is no fee on transferFrom() (like potentially on USDT)

    @Notes:


    @Link:

*/
rule noFeeOnTransferFrom(address alice, address bob, uint256 amount) {
    env e;
    require alice != bob;
    // require allowance(alice, e.msg.sender) >= amount;
    mathint balanceBefore = balanceOf(bob);
    mathint balanceAliceBefore = balanceOf(alice);

    bool sucsess = transferFrom(e, alice, bob, amount);

    mathint balanceAfter = balanceOf(bob);
    mathint balanceAliceAfter = balanceOf(alice);
    assert sucsess => balanceAfter == balanceBefore + amount;
    assert sucsess => balanceAliceAfter == balanceAliceBefore - amount;
    assert !sucsess => balanceAfter == balanceBefore;
    assert !sucsess => balanceAliceAfter == balanceAliceBefore;
}


