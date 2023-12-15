methods {
    // ERC20 functionality
    function _transfer(address, address, uint256) internal;
    function transfer(address, uint256) external returns (bool);
    function transferFrom(address, address, uint256) external returns (bool);
    function approve(address, uint256) external returns (bool);
    function permit(address, address, uint256, uint256, uint8, bytes32, bytes32) external returns (bool);

    // Getters: 
    function allowance(address, address) external returns (uint256) envfree;
    function balanceOf(address) external returns (uint256) envfree;
    function totalSupply() external returns (uint256) envfree;

    // Stableswap functionality
    function last_price() external returns(uint256) envfree;
    function ema_price() external returns(uint256) envfree;
    function get_balances() external returns(uint256[2]) envfree;
    function admin_fee() external returns(uint256) envfree;
    function A() external returns(uint256);
    function A_precise() external returns(uint256);
    function get_p() external returns(uint256);
    function price_oracle() external returns(uint256);
    function get_virtual_price() external returns(uint256);
    function calc_token_amount(uint256[], bool) external returns(uint256);
    function add_liquidity(uint256[], uint256, address) external returns(uint256);
    function remove_liquidity(uint256, uint256[], address) external returns(uint256[]);
    function remove_liquidity_imbalance(uint256[], uint256, address) external returns(uint256[]);
    function get_dy(int128, int128, uint256) external returns(uint256) envfree;
    function get_dx(int128, int128, uint256) external returns(uint256) envfree;
    function exchange(int128, int128, uint256, uint256, address) external returns(uint256);
    function calc_withdraw_one_coin(uint256, int128) external returns(uint256);
    function ramp_A(uint256, uint256) external;
    function stop_ramp_A() external;
    function set_ma_exp_time(uint256) external;
    function admin_balances(uint256) external returns(uint256);
    function commit_new_fee(uint256) external;
    function apply_new_fee() external;
    function withdraw_admin_fees() external;
}

// /* 
// 	Property: Find and show a path for each method.
// */
// rule reachability(method f)
// {
// 	env e;
// 	calldataarg args;
// 	f(e,args);
// 	satisfy true;
// }



/* 
   	Property: Define and check functions that should never revert
	Notice:  use f.selector to state which functions should not revert,e.g.f.selector == sig:balanceOf(address).selector 
*/  
definition nonReveritngFunction(method f ) returns bool = 
    f.selector == sig:balanceOf(address).selector ||
    f.selector == sig:allowance(address, address).selector ||
    f.selector == sig:totalSupply().selector; 

definition canIncreaseAllowance(method f ) returns bool = 
	f.selector == sig:approve(address,uint256).selector || 
	f.selector == sig:permit(address, address, uint256, uint256, uint8, bytes32, bytes32).selector;

definition canDecreaseAllowance(method f ) returns bool = 
	f.selector == sig:approve(address,uint256).selector || 
	f.selector == sig:permit(address, address, uint256, uint256, uint8, bytes32, bytes32).selector ||
	f.selector == sig:transferFrom(address,address,uint256).selector;

definition canIncreaseBalance(method f ) returns bool = 
	f.selector == sig:transfer(address,uint256).selector ||
	f.selector == sig:transferFrom(address,address,uint256).selector ||
    f.selector == sig:add_liquidity(uint256[2], uint256, address).selector ||
    f.selector == sig:add_liquidity(uint256[2], uint256).selector;

definition canDecreaseBalance(method f ) returns bool = 
	f.selector == sig:transfer(address,uint256).selector ||
	f.selector == sig:transferFrom(address,address,uint256).selector ||
    f.selector == sig:remove_liquidity(uint256, uint256[2], address).selector ||
    f.selector == sig:remove_liquidity(uint256, uint256[2]).selector ||
    f.selector == sig:remove_liquidity_imbalance(uint256[2], uint256, address).selector ||
    f.selector == sig:remove_liquidity_imbalance(uint256[2], uint256).selector ||
    f.selector == sig:remove_liquidity_one_coin(uint256,int128,uint256,address).selector ||
    f.selector == sig:remove_liquidity_one_coin(uint256,int128,uint256).selector;

definition priveledgedFunction(method f ) returns bool = false;

definition canIncreaseTotalSupply(method f ) returns bool = 
    f.selector == sig:add_liquidity(uint256[2], uint256, address).selector ||
    f.selector == sig:add_liquidity(uint256[2], uint256).selector;

definition canDecreaseTotalSupply(method f ) returns bool = 
    f.selector == sig:remove_liquidity(uint256, uint256[2], address).selector ||
    f.selector == sig:remove_liquidity(uint256, uint256[2]).selector ||
    f.selector == sig:remove_liquidity_imbalance(uint256[2], uint256, address).selector ||
    f.selector == sig:remove_liquidity_imbalance(uint256[2], uint256).selector ||
    f.selector == sig:remove_liquidity_one_coin(uint256,int128,uint256,address).selector ||
    f.selector == sig:remove_liquidity_one_coin(uint256,int128,uint256).selector;

/*
	List of functions we assume are allowd to change the [totalSupply]
*/

definition canChangeTotalSupply(method f ) returns bool = 
    f.selector == sig:add_liquidity(uint256[2], uint256, address).selector ||
    f.selector == sig:add_liquidity(uint256[2], uint256).selector ||
    f.selector == sig:remove_liquidity(uint256, uint256[2], address).selector ||
    f.selector == sig:remove_liquidity(uint256, uint256[2]).selector ||
    f.selector == sig:remove_liquidity_imbalance(uint256[2], uint256, address).selector ||
    f.selector == sig:remove_liquidity_imbalance(uint256[2], uint256).selector ||
    f.selector == sig:remove_liquidity_one_coin(uint256,int128,uint256,address).selector ||
    f.selector == sig:remove_liquidity_one_coin(uint256,int128,uint256).selector;

// PASS
rule transferFromChangesBalanceAndAllowanceCorrectly() {
	env e;
	address spender = e.msg.sender;
	address owner;
	address recipient;

	uint256 allowedBefore = allowance(owner, spender);
    require allowedBefore < max_uint256; // Max value behaves like infinity in the Stableswap.
	uint256 ownerBalanceBefore = balanceOf(owner);
	uint256 recipientBalanceBefore = balanceOf(recipient);
	uint256 transfered;

	transferFrom(e, owner, recipient, transfered);

	if (allowedBefore < max_uint256) {
		assert allowedBefore == assert_uint256(allowance(owner, spender) + transfered);
	} else {
		assert allowance(owner, spender) == max_uint256;
	}

	if(owner == recipient) {
		assert assert_uint256(ownerBalanceBefore) == balanceOf(owner);
	} else { 
		assert assert_uint256(ownerBalanceBefore - transfered) == balanceOf(owner);
		assert assert_uint256(recipientBalanceBefore + transfered) == balanceOf(recipient);
	}
}

// PASS
rule transferFromRevertingConditions() {
    address owner;
	env e;
	require e.msg.value == 0;
	address spender = e.msg.sender;
	address recipient;

	uint256 allowed = allowance(owner, spender);
	uint256 transfered;

    bool allowanceIsLow = allowed < transfered;
    bool notEnoughBalance = balanceOf(owner) < transfered;
    bool overflow = recipient != owner && balanceOf(recipient) + transfered > max_uint;

    bool shouldRevert = allowanceIsLow || notEnoughBalance || overflow;

    transferFrom@withrevert(e, owner, recipient, transfered);   
	assert lastReverted <=> shouldRevert;	
}

// PASS
rule approveSetsAllowance() {
	env e;
	address spender;
	address owner = e.msg.sender;
	uint amount;

	approve(e, spender, amount);
	uint256 allowed = allowance(owner, spender);
	assert allowed == amount;
}

// PASS
rule approveDoesNotRevert() {
    env e;
	require e.msg.value == 0;
	address spender;
	address owner = e.msg.sender;
	uint amount;

    // Does not revert for owner == 0 nor spender == 0
	// bool zeroAddress = owner == 0 || spender == 0;
	// bool shouldRevert = zeroAddress;
    bool shouldRevert = false;
    
	approve@withrevert(e, spender, amount);
	assert lastReverted == shouldRevert;
}

// PASS
rule transferChangesBalanceCorrectly() {
	env e;
    address recipient;
    uint256 amount;

    mathint balanceOfRecipientBefore = balanceOf(recipient);
    mathint balanceOfSenderBefore = balanceOf(e.msg.sender);

    transfer(e, recipient, amount);

	if(e.msg.sender != recipient) {
		assert balanceOf(e, recipient) == assert_uint256(balanceOfRecipientBefore + amount);
		assert balanceOf(e, e.msg.sender) == assert_uint256(balanceOfSenderBefore - amount);
	} else {
		assert balanceOf(e, e.msg.sender) == assert_uint256(balanceOfSenderBefore);
	}
}

// PASS
rule transferRevertingConditions {
	env e;
	address recipient;
	uint256 amount;
    require e.msg.value == 0;

	bool senderBalanceTooLow = balanceOf(e.msg.sender) < amount;
    // bool zeroRecipient = recipient == 0;
    bool zeroSender = e.msg.sender == 0;
    bool senderIsRecipient = e.msg.sender == recipient;

    bool recipientBalanceOverflows = balanceOf(recipient) + amount > max_uint256 && !senderIsRecipient;

    // bool shouldRevert = senderBalanceTooLow || zeroRecipient || zeroSender || recipientBalanceOverflows;
    bool shouldRevert = senderBalanceTooLow || recipientBalanceOverflows;

	transfer@withrevert(e, recipient, amount);
	assert lastReverted <=> shouldRevert;
}



//
// In the following part, we check for every variable (e.g. balances or allowance) that:
// 1. they can be changed only by privileged methods, and
// 2. the privileged methods might change variables corresponding only to the users 
// 	that call the methods
//


/*
	Functions that are not not allowed to change the [totalSupply] (via [canChangeTotalSupply()])
	do not change the total balance.
*/
// PASS
rule totalSupplyDoesNotChange(method f) filtered {f -> !canChangeTotalSupply(f) } 
{		
	env e;
	calldataarg args;

	uint256 before = totalSupply(e);
	f(e,args);
    uint256 after = totalSupply(e);
	assert before == after;
}


/*
	The below function just calls (dispatch) all methods (an arbitrary one) from the contract, 
	using given [env e], [address from] and [address to].
	We use this function in several rules, including: . The usecase is typically to show that 
	the call of the function does not affect a "property" of a third party (i.e. != e.msg.sender, from, to),
	such as the balance or allowance.  

*/
function callFunctionWithParams(env e, method f, address from, address to) {
	uint256 amount;

	if (f.selector == sig:transfer(address, uint256).selector) {
		require from == e.msg.sender;
		transfer(e, to, amount);
	} else if (f.selector == sig:allowance(address, address).selector) {
		allowance(e, from, to);
	} else if (f.selector == sig:approve(address, uint256).selector) {
		approve(e, to, amount);
	} else if (f.selector == sig:transferFrom(address, address, uint256).selector) {
		transferFrom(e, from, to, amount);
	} else if (f.selector == sig:permit(address, address, uint256, uint256, uint8, bytes32, bytes32).selector) {
        uint256 deadline; uint8 _v; bytes32 _r; bytes32 _s;
        permit(e, from, to, amount, deadline, _v, _r, _s);
    } else if (f.selector == sig:add_liquidity(uint256[2], uint256, address).selector) {
		uint256[2] amounts;
		add_liquidity(e, amounts, amount, to);
	} else {
		calldataarg args;
		f(e, args);
	}
}


function callLiquidityFunctionsWithAddress(env e, method f, address receiver) {
	uint256[2] amounts;
	uint256 amount;
	int128 coinIndex;

	if (f.selector == sig:add_liquidity(uint256[2], uint256, address).selector) {
		add_liquidity(e, amounts, amount, receiver);
	} else if (f.selector == sig:remove_liquidity(uint256, uint256[2], address).selector) {
		remove_liquidity(e, amount, amounts, receiver);
	} else if (f.selector == sig:remove_liquidity_imbalance(uint256[2], uint256, address).selector) {
		remove_liquidity_imbalance(e, amounts, amount, receiver);
	} else if (f.selector == sig:remove_liquidity_one_coin(uint256,int128,uint256,address).selector) {
		uint256 burnAmount;
		remove_liquidity_one_coin(e, burnAmount, coinIndex, amount, receiver);
	}
}

/*
	Given addresses [e.msg.sender], [from], [to] and [thirdParty], we check that 
	there is no method [f] that would:
	1] not take [thirdParty] as an input argument, and
	2] yet changed the balance of [thirdParty].
	Intuitively, we target e.g. the case where a transfer of tokens [from] -> [to]
	changes the balance of [thirdParty]. 
*/
// PASS
rule doesNotAffectAThirdPartyBalance(method f) {
	env e;	
	address from;
	address to;
	address thirdParty;

	require (thirdParty != from) && (thirdParty != to) && (thirdParty != e.msg.sender);

	uint256 thirdBalanceBefore = balanceOf(e, thirdParty);
	callFunctionWithParams(e, f, from, to);

	assert balanceOf(e, thirdParty) == thirdBalanceBefore;
}

/*
	Given addresses [e.msg.sender], [from], [to] and [thirdParty], we check that 
	there is no method [f] that would:
	1] not take [thirdParty] as an input argument, and
	2] yet changed the allowance of [thirdParty] w.r.t a [thirdPartySpender].
*/
// PASS
rule doesNotAffectAThirdPartyAllowance(method f) {
	env e;	
	address from;
	address to;
	address thirdParty;
	address thirdPartySpender;

	require (thirdParty != from) && (thirdParty != to) && (thirdParty != e.msg.sender);

	uint256 spenderAllowanceBefore = allowance(e, thirdParty, thirdPartySpender);
	callFunctionWithParams(e, f, from, to);
    require f.selector != sig:permit(address, address, uint256, uint256, uint8, bytes32, bytes32).selector;

	assert allowance(e, thirdParty, thirdPartySpender) == spenderAllowanceBefore;
}

// PASS
rule onlyAllowedMethodsMayChangeBalance(method f) {
	env e;
	address addr;
	uint256 balanceBefore = balanceOf(addr);
	calldataarg args;
	f(e,args);
	uint256 balanceAfter = balanceOf(addr);
	assert balanceAfter > balanceBefore => canIncreaseBalance(f), "should not increase balance";
	assert balanceAfter < balanceBefore => canDecreaseBalance(f), "should not decrease balance";
}

/*
	Checks that functions that can change the balance change balance only of the relevant adresses, 
	i.e, do not affect a third party. For example, burn(...) should decrease a balance only of a single address.
*/
// PASS
rule whoCanChangeBalance(method f) filtered {f -> canDecreaseBalance(f) || canIncreaseBalance(f) } {
	env e;
	address mightChange;
	address shouldNotChange;
	require mightChange != shouldNotChange;
	uint256 balanceBefore = balanceOf(shouldNotChange);
	
	uint256 amount;
	address receiver;
	require receiver != shouldNotChange;

	if (f.selector == sig:transfer(address,uint256).selector) {
		require e.msg.sender == mightChange;
		transfer(e, receiver, amount);
	} else if (f.selector == sig:transferFrom(address,address,uint256).selector) {
		transferFrom(e, mightChange, receiver, amount);
	} else if (f.selector == sig:add_liquidity(uint256[2], uint256).selector ||
			f.selector == sig:remove_liquidity(uint256, uint256[2]).selector ||
			f.selector == sig:remove_liquidity_imbalance(uint256[2], uint256).selector ||
			f.selector == sig:remove_liquidity_one_coin(uint256,int128,uint256).selector
	) {
		require e.msg.sender == mightChange;
		calldataarg args;
		f(e,args);
	} else if (f.selector == sig:add_liquidity(uint256[2], uint256, address).selector ||
			f.selector == sig:remove_liquidity(uint256, uint256[2], address).selector ||
    		f.selector == sig:remove_liquidity_imbalance(uint256[2], uint256, address).selector ||
    		f.selector == sig:remove_liquidity_one_coin(uint256,int128,uint256, address).selector
	) {
		require e.msg.sender == mightChange;
		callLiquidityFunctionsWithAddress(e, f, receiver);
	}
	else {
		// This is here to trigger when user adds a new function to the smart contract that
		// can change the balance. In such case, we should include corresponding [else if] here.
		assert false;
	}

	assert balanceBefore == balanceOf(shouldNotChange);
}

// PASS
rule onlyAllowedMethodsMayChangeAllowance(method f) {
	env e;
	address addr1;
	address addr2;
	uint256 allowanceBefore = allowance(addr1, addr2);
	calldataarg args;
	f(e,args);
	uint256 allowanceAfter = allowance(addr1, addr2);
	assert allowanceAfter > allowanceBefore => canIncreaseAllowance(f), "should not increase allowance";
	assert allowanceAfter < allowanceBefore => canDecreaseAllowance(f), "should not decrease allowance";
}

/*
	Checks that functions that can change the balance change balance only of the relevant adresses, 
	i.e, do not affect a third party. For example, burn(...) should decrease a balance only of a single address.
*/
// PASS
rule whoCanChangeAllowance(method f) filtered { f -> (canDecreaseAllowance(f) || canIncreaseAllowance(f)) && f.selector != sig:permit(address,address,uint256,uint256,uint8,bytes32,bytes32).selector} {
	env e;
	address owner;
	address spender;
	uint256 amountToChange;	

	address otherOwner;
	address otherSpender;
	uint256 theOtherAllowance = allowance(otherOwner, otherSpender);
    
	if(f.selector == sig:approve(address,uint256).selector) {		
		require owner == e.msg.sender;
		uint256 newAllowance;
		require to_mathint(amountToChange) == allowance(owner, spender) - newAllowance;
		approve(e, spender, newAllowance);
	} else if(f.selector == sig:transferFrom(address,address,uint256).selector) {
		address recipient;
		require e.msg.sender == spender;
		transferFrom(e, owner, recipient, amountToChange);
	} else {
		// This is here to trigger when user adds a new function to the smart contract that
		// can change the balance. In such case, we should include corresponding [else if] here.
		assert false;
	}

	uint256 newAllowanceOfTheOther = allowance(otherOwner, otherSpender);

	assert theOtherAllowance != newAllowanceOfTheOther <=>
		(otherSpender == spender &&
		 otherOwner == owner &&
		 amountToChange > 0 &&
		 (f.selector == sig:transferFrom(address,address,uint256).selector => theOtherAllowance < max_uint256)
		);
}

// PASS
rule onlyAllowedMethodsMayChangeTotalSupply(method f) {
	env e;
	uint256 totalSupplyBefore = totalSupply();
	calldataarg args;
	f(e,args);
	uint256 totalSupplyAfter = totalSupply();
	assert totalSupplyAfter > totalSupplyBefore => canIncreaseTotalSupply(f), "should not increase total supply";
	assert totalSupplyAfter < totalSupplyBefore => canDecreaseTotalSupply(f), "should not decrease total supply";
}


invariant ZeroAddressNoBalance()
    balanceOf(0) == 0;


/*

invariant balanceOfZeroIsZero()
	balanceOf(0) == 0;

ghost mathint sumOfBalances {
	init_state axiom sumOfBalances == 0;
}

ghost mathint totalWithdraw {
	init_state axiom totalWithdraw == 0;
}

ghost mathint totalDeposit {
	init_state axiom totalDeposit == 0;
}


hook Sstore balanceOf[KEY address a] uint new_value (uint old_value) STORAGE {
	sumOfBalances = sumOfBalances + new_value - old_value;
	numberOfChangesOfBalances = numberOfChangesOfBalances + 1;
}

invariant totalSupplyIsSumOfBalances()
	to_mathint(totalSupply()) == sumOfBalances;

ghost mathint numberOfChangesOfBalances {
	init_state axiom numberOfChangesOfBalances == 0;
}

rule noMethodChangesMoreThanTwoBalances(method f) {
	env e;
	mathint numberOfChangesOfBalancesBefore = numberOfChangesOfBalances;
	calldataarg args;
	f(e,args);
	mathint numberOfChangesOfBalancesAfter = numberOfChangesOfBalances;
	assert numberOfChangesOfBalancesAfter <= numberOfChangesOfBalancesBefore + 2;
}


invariant positiveBalance()
	totalWithdraw <= totalDeposit
	filtered {f -> f.selector != sig:remove_liquidity(uint256, uint256[2], address).selector &&
    f.selector != sig:remove_liquidity(uint256, uint256[2]).selector &&
    f.selector != sig:remove_liquidity_imbalance(uint256[2], uint256, address).selector &&
    f.selector != sig:remove_liquidity_imbalance(uint256[2], uint256).selector &&
    f.selector != sig:remove_liquidity_one_coin(uint256,int128,uint256,address).selector &&
    f.selector != sig:remove_liquidity_one_coin(uint256,int128,uint256).selector}


	*/