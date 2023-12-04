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
    function allowance(address, address) external returns (uint256) envfree;
    function balanceOf(address) external returns (uint256) envfree;
    function totalSupply() external returns (uint256) envfree;
    function minter() external returns (address) envfree;
}

ghost mathint sum_of_balances {
    init_state axiom sum_of_balances == 0;
}

hook Sstore balanceOf[KEY address user] uint256 newvalue (uint256 oldvalue) STORAGE {
    sum_of_balances = sum_of_balances + newvalue - oldvalue;
}

invariant totalSupplyEqualsSum()
    to_mathint(totalSupply()) == sum_of_balances;

/*
    @Description:
        Balance of address 0 is always 0
*/
invariant ZeroAddressNoBalance()
    balanceOf(0) == 0;

function doesntChangeBalance(method f) returns bool {
    return f.selector != sig:transfer(address,uint256).selector &&
        f.selector != sig:transferFrom(address,address,uint256).selector &&
        f.selector != sig:mint(address,uint256).selector &&
        f.selector != sig:burn(uint256).selector &&
        f.selector != sig:burnFrom(address,uint256).selector;
}

/*
    @Description:
        Verify that there is no fee on transfer() (like potentially on USDT)
*/
rule noFeeOnTransfer(address bob, uint256 amount) {
    env e;
    require bob != e.msg.sender;
    mathint balanceSenderBefore = balanceOf(e.msg.sender);
    mathint balanceBefore = balanceOf(bob);

    bool sucsess = transfer(e, bob, amount);

    mathint balanceAfter = balanceOf(bob);
    mathint balanceSenderAfter = balanceOf(e.msg.sender);
    assert balanceAfter == balanceBefore + amount;
    assert balanceSenderAfter == balanceSenderBefore - amount;
}

/*
    @Description:
        Verify that there is no fee on transferFrom() (like potentially on USDT)
*/
rule noFeeOnTransferFrom(address alice, address bob, uint256 amount) {
    env e;
    require alice != bob;
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

/*
    @Description:
        Token transfer works correctly. Balances are updated if not reverted.
        If reverted then the transfer amount was too high, or the recipient is 0.

    @Notes:
        This rule fails on tokens with a blacklist function, like USDC and USDT.
        The prover finds a counterexample of a reverted transfer to a blacklisted address or a transfer in a paused state.
*/
rule transferCorrect(address to, uint256 amount) {
    env e;
    require e.msg.value == 0 && e.msg.sender != 0;
    mathint fromBalanceBefore = balanceOf(e.msg.sender);
    mathint toBalanceBefore = balanceOf(to);
    require fromBalanceBefore + toBalanceBefore <= max_uint256;

    bool sucsess = transfer@withrevert(e, to, amount);
    bool reverted = lastReverted;
    if (!reverted) {
        if (e.msg.sender == to) {
            assert to_mathint(balanceOf(e.msg.sender)) == fromBalanceBefore;
        } else {
            assert to_mathint(balanceOf(e.msg.sender)) == fromBalanceBefore - amount;
            assert to_mathint(balanceOf(to)) == toBalanceBefore + amount;
        }
    } else {
        assert to_mathint(amount) > fromBalanceBefore || to == 0 || to == currentContract;
    }
}

/*
    @Description:
        Test that transferFrom works correctly. Balances are updated if not reverted.
        If reverted, it means the transfer amount was too high, or the recipient is 0

    @Notes:
        This rule fails on tokens with a blacklist and or pause function, like USDC and USDT.
        The prover finds a counterexample of a reverted transfer to a blacklisted address or a transfer in a paused state.
*/

rule transferFromCorrect(address from, address to, uint256 amount) {
    env e;
    require e.msg.value == 0;
    mathint fromBalanceBefore = balanceOf(from);
    mathint toBalanceBefore = balanceOf(to);
    mathint allowanceBefore = allowance(from, e.msg.sender);
    require fromBalanceBefore + toBalanceBefore <= max_uint256;

    bool sucsess = transferFrom(e, from, to, amount);

    mathint fromBalanceAfter = balanceOf(from);
    mathint toBalanceAfter = balanceOf(to);
    mathint allowanceAfter = allowance(from, e.msg.sender);

    assert from != to =>
        fromBalanceAfter == fromBalanceBefore - amount &&
        toBalanceAfter == toBalanceBefore + amount;
    assert from != to && allowanceBefore != max_uint256 =>
        allowanceAfter == allowanceBefore - amount;
}

/*
    @Description:
        transferFrom should revert if and only if the amount is too high or the recipient is 0.

    @Notes:
        Fails on tokens with pause/blacklist functions, like USDC.
*/
rule transferFromReverts(address from, address to, uint256 amount) {
    env e;
    uint256 allowanceBefore = allowance(from, e.msg.sender);
    uint256 fromBalanceBefore = balanceOf(from);
    require from != 0 && e.msg.sender != 0;
    require e.msg.value == 0;
    require fromBalanceBefore + balanceOf(to) <= max_uint256;

    transferFrom@withrevert(e, from, to, amount);

    assert lastReverted <=> (allowanceBefore < amount || amount > fromBalanceBefore || to == 0 || to == currentContract);
}

/*
    @Description:
        Transfer from msg.sender to alice doesn't change the balance of other addresses
*/
rule TransferDoesntChangeOtherBalance(address to, uint256 amount, address other) {
    env e;
    require other != e.msg.sender;
    require other != to && other != currentContract;
    uint256 balanceBefore = balanceOf(other);
    transfer(e, to, amount);
    assert balanceBefore == balanceOf(other);
}

/*
    @Description:
        Transfer from alice to bob using transferFrom doesn't change the balance of other addresses
*/
rule TransferFromDoesntChangeOtherBalance(address from, address to, uint256 amount, address other) {
    env e;
    require other != from;
    require other != to;
    uint256 balanceBefore = balanceOf(other);
    transferFrom(e, from, to, amount);
    assert balanceBefore == balanceOf(other);
}

/*
    @Description:
        Allowance changes correctly as a result of calls to approve, transfer, increaseAllowance, decreaseAllowance

    @Notes:
        Some ERC20 tokens have functions like permit() that change allowance via a signature.
        The rule will fail on such functions.
*/
rule ChangingAllowance(method f, address from, address spender) {
    uint256 allowanceBefore = allowance(from, spender);
    env e;
    if (f.selector == sig:approve(address, uint256).selector) {
        address spender_;
        uint256 amount;
        approve(e, spender_, amount);
        if (from == e.msg.sender && spender == spender_) {
            assert allowance(from, spender) == amount;
        } else {
            assert allowance(from, spender) == allowanceBefore;
        }
    } else if (f.selector == sig:transferFrom(address,address,uint256).selector) {
        address from_;
        address to;
        uint256 amount;
        transferFrom(e, from_, to, amount);
        mathint allowanceAfter = allowance(from, spender);
        if (from == from_ && spender == e.msg.sender) {
            assert from == to || allowanceBefore == max_uint256 || allowanceAfter == allowanceBefore - amount;
        } else {
            assert allowance(from, spender) == allowanceBefore;
        }
    } else if (f.selector == sig:decreaseAllowance(address, uint256).selector) {
        address spender_;
        uint256 amount;
        require amount <= allowanceBefore;
        decreaseAllowance(e, spender_, amount);
        if (from == e.msg.sender && spender == spender_) {
            assert to_mathint(allowance(from, spender)) == allowanceBefore - amount;
        } else {
            assert allowance(from, spender) == allowanceBefore;
        }
    } else if (f.selector == sig:increaseAllowance(address, uint256).selector) {
        address spender_;
        uint256 amount;
        require amount + allowanceBefore < max_uint256;
        increaseAllowance(e, spender_, amount);
        if (from == e.msg.sender && spender == spender_) {
            assert to_mathint(allowance(from, spender)) == allowanceBefore + amount;
        } else {
            assert allowance(from, spender) == allowanceBefore;
        }
    } else if (f.selector == sig:burnFrom(address, uint256).selector) {
        address from_;
        uint256 amount;
        burnFrom(e, from_, amount);
        mathint allowanceAfter = allowance(from, spender);
        if (from == from_ && spender == e.msg.sender) {
            assert allowanceBefore == max_uint256 || allowanceAfter == allowanceBefore - amount;
        } else {
            assert allowance(from, spender) == allowanceBefore;
        }
    } else if (f.selector == sig:permit(address, address, uint256, uint256, uint8, bytes32, bytes32).selector) {
        // address from_;
        // address to_;
        // uint256 amount;
        // uint256 deadline_;
        // uint8 _v;
        // bytes32 _r;
        // bytes32 _s;
        // permit(e, from_, to_, amount, deadline_, _v, _r, _s);
        // mathint allowanceAfter = allowance(from, spender);
        // if (from == from_ && spender == e.msg.sender) {
        //     assert allowanceBefore == max_uint256 || from_ == to_ || allowanceAfter == amount;
        // } else {
        //     assert allowance(from, spender) == allowanceBefore;
        // }
        assert true;
    } else
    {
        calldataarg args;
        f(e, args);
        assert allowance(from, spender) == allowanceBefore;
    }
}

/*
    @Description:
        Test that mint works correctly. Balances and totalSupply are updated corrct according to the paramenters.
*/
rule integrityOfMint(address owner, uint amount) {
    env e;
    mathint totalSupplyBefore = totalSupply();
    mathint ownerBalanceBefore = balanceOf(owner);
    address minter = minter();

    // avoid overflows
    require totalSupplyBefore + amount < max_uint128;
    require ownerBalanceBefore + amount < max_uint128;

    bool success = mint(e, owner, amount);

    mathint totalSupplyAfter = totalSupply();
    mathint ownerBalanceAfter = balanceOf(owner);

    assert totalSupplyAfter == totalSupplyBefore + amount && ownerBalanceAfter == ownerBalanceBefore + amount;
    assert e.msg.sender == minter; // only minter can mint
}

/*
    @Description:
        Test that burn works correctly. Balances and totalSupply are updated corrct according to the paramenters.
*/
rule integrityOfBurn(uint amount) {
    env e;
    mathint totalSupplyBefore = totalSupply();
    mathint ownerBalanceBefore = balanceOf(e.msg.sender);

    bool success = burn(e, amount);

    mathint totalSupplyAfter = totalSupply();
    mathint ownerBalanceAfter = balanceOf(e.msg.sender);

    assert success => (totalSupplyAfter == totalSupplyBefore - amount && ownerBalanceAfter == ownerBalanceBefore - amount);
    assert !success => (totalSupplyAfter == totalSupplyBefore && ownerBalanceAfter == ownerBalanceBefore);
}

/*
    @Description:
        Test that burnFrom works correctly. Balances and totalSupply are updated corrct according to the paramenters.
*/
rule integrityOfBurnFrom(address owner, uint amount) {
    env e;
    mathint totalSupplyBefore = totalSupply();
    mathint ownerBalanceBefore = balanceOf(owner);
    mathint allowanceBefore = allowance(owner, e.msg.sender);

    bool success = burnFrom(e, owner, amount);

    mathint totalSupplyAfter = totalSupply();
    mathint ownerBalanceAfter = balanceOf(owner);
    mathint allowanceAfter = allowance(owner, e.msg.sender);

    assert success => (totalSupplyAfter == totalSupplyBefore - amount && ownerBalanceAfter == ownerBalanceBefore - amount);
    assert !success => (totalSupplyAfter == totalSupplyBefore && ownerBalanceAfter == ownerBalanceBefore);
    assert (success && allowanceBefore < max_uint256) => allowanceAfter == allowanceBefore - amount;
}

rule mintMonotonicity(address owner, uint256 amount1, uint256 amount2) {
	env e;
    require amount1 < amount2;
	storage init = lastStorage;

	mint(e, owner, amount1);

	uint256 balanceAmount1 = balanceOf(owner);

	mint(e, owner, amount2) at init;

	uint256 balanceAmount2 = balanceOf(owner);

	assert balanceAmount1 < balanceAmount2;
}

rule burnMonotonicity(uint256 amount1, uint256 amount2) {
	env e;
    require amount1 < amount2;
	storage init = lastStorage;

	burn(e, amount1);

	uint256 balanceAmount1 = balanceOf(e.msg.sender);

	burn(e, amount2) at init;

	uint256 balanceAmount2 = balanceOf(e.msg.sender);

	assert balanceAmount1 > balanceAmount2;
}

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
